import boto3
import bz2
import hashlib
import json
import io
import os
import traceback
from threading import Lock
from time import time
from concurrent.futures import ThreadPoolExecutor
from lib.db_driven_task import DBDrivenTaskProcessor, DBTask
from lib.monitor import timeit, MultiprocessMonitor
from lib.blame_game import BlameGameRetriever
from w3hn.dependency.golang import GoDependencyAnalyzer
from w3hn.dependency.scala import ScalaDependencyAnalyzer
from w3hn.dependency.java import JavaDependencyAnalyzer
from w3hn.dependency.python import PythonDependencyAnalyzer
from w3hn.dependency.javascript import JavascriptDependencyAnalyzer


def add_int_to_map(map, key, value):
    if key not in map:
        map[key] = 0
    map[key] += value


def add_int_key_value_submap_to_map(map, root_key, sub_key, value, init_value=0):
    if isinstance(root_key, int) or isinstance(sub_key, int):
        print('Something is NOT right:' + str(root_key) + ' ' + str(sub_key))
    if root_key not in map.keys():
        map[root_key] = {}
    if sub_key not in map[root_key].keys():
        map[root_key][sub_key] = init_value
    map[root_key][sub_key] += value


class RepoAnalyzer(DBDrivenTaskProcessor):
    def get_timeout(self):
        return time()-self.expire_time if self.expire_time else -1

    def init(self):
        if self.monitor is None:
            self.monitor = MultiprocessMonitor()
        kwargs = {'tmout': self.get_timeout}
        self.monitor.add_display_item(**kwargs)

    def __init__(self, **kwargs):
        DBDrivenTaskProcessor.__init__(self, **kwargs)
        self.expire_time = None
        self.repo_dependency_map = None
        self.hacker_name_to_md5_map = None
        self.commit_to_hacker_map = None
        self.get_next = self.GetNextRepoForAnalysis(self)
        self.all_done = self.ReleaseRepo(self)
        self.repo_owner = None
        self.repo_name = None

        self.repo_id = None
        self.repo_owner = None
        self.repo_name = None
        self.repo_dir = None
        self.numstat_dir = None
        self.numstat = None
        self.numstat_raw = None
        self.numstat_str = None
        self.numstat_json = None
        self.extension_map = None
        self.filename_map = None
        self.stats_json = None
        self.cur_job = 'Starting...'
        self.find_orphan_sql = None
        self.hacker_name_map = None
        self.s3r = boto3.resource('s3')
        self.bucket = self.s3r.Bucket('numstat-bucket')
        self.hacker_extension_map = None
        self.hacker_md5_map = None
        self.hacker_file_map = None
        self.filename_blame_map = None
        self.blame_game_retriever = None
        self.import_map_map = {}
        self.dependency_list = [JavaDependencyAnalyzer(), GoDependencyAnalyzer(), PythonDependencyAnalyzer(),
                                ScalaDependencyAnalyzer(), JavascriptDependencyAnalyzer()]
        self.max_threads_key = 'REPO_ANALYZER_MAX_THREADS'
        self.max_threads = int(os.environ[self.max_threads_key]) if \
            self.max_threads_key in os.environ.keys() and \
              os.environ[self.max_threads_key] else None

    class GetNextRepoForAnalysis(DBTask):
        def __init__(self, mom):
            self.mom = mom

        def get_proc_name(self):
            return 'ReserveNextRepoForAnalysis'

        def get_proc_parameters(self):
            return [self.mom.machine_name]

        def process_db_results(self, result_args):
            result = None
            for goodness in self.mom.cursor.stored_results():
                result = goodness.fetchone()
                if result:
                    self.mom.repo_id = int(result[0])
                    self.mom.repo_owner = result[1]
                    self.mom.repo_name = result[2]
                    self.mom.repo_dir = result[3] if result[3] else os.path.join('./repos/', self.mom.repo_owner, self.mom.repo_name)
                    self.mom.numstat_dir = result[4] if result[4] else os.path.join('./results/', self.mom.repo_owner, self.mom.repo_name)
                    self.mom.cur_job = result[1] + ':' + result[2]
            if result is None:
                self.mom.cur_job = 'Nada'
            return result

    class ReleaseRepo(DBTask):
        def __init__(self, mom):
            self.mom = mom

        def get_proc_name(self):
            return 'ReleaseRepoFromAnalysis'

        def get_proc_parameters(self):
            return [self.mom.repo_id, self.mom.success, self.mom.stats_json]

        def process_db_results(self, result_args):
            return True

    def get_job_fetching_task(self):
        return self.get_next

    def get_job_completion_task(self):
        return self.all_done

    @timeit
    def parse_json(self):
        self.extension_map = {}
        self.filename_map = {}
        self.hacker_extension_map = {}
        self.hacker_md5_map = {}
        self.hacker_name_map = {}
        self.commit_to_hacker_map = {}
        self.hacker_file_map = {}
        self.filename_blame_map = {}
        self.hacker_name_to_md5_map = {}

        for commit in self.numstat:
            author = commit['Author']
            commit_id = commit['commit']
            try:
                author_md5 = hashlib.md5(author.encode('utf-8')).hexdigest()
            except Exception as e:
                print(e)
                traceback.print_exc()
                b = bytearray(author, 'unicode-escape')
                author_md5 = hashlib.md5(b).hexdigest()
            if author_md5 not in self.hacker_extension_map:
                self.hacker_extension_map[author_md5] = {}
                self.hacker_name_map[author_md5] = author
                self.hacker_file_map[author_md5] = {}
                self.hacker_name_to_md5_map[author] = author_md5
            self.commit_to_hacker_map[commit_id] = author_md5

    @timeit
    def prepare_sql_params(self):
        self.stats_json = {'hacker_name_map': self.hacker_name_map}
        self.stats_json = json.dumps(self.stats_json, ensure_ascii=False)

    @timeit
    def process_task(self):
        self.success = False
        self.expire_time = time() + (60 * 30)
        try:
            if os.path.exists(self.numstat_dir):
                with open(self.numstat_dir, 'rb') as r:
                    self.numstat_raw = r.read()
                self.numstat_json = bz2.decompress(self.numstat_raw)
                self.numstat = json.loads(self.numstat_json)

                key = 'repo/'+self.repo_owner+'/'+self.repo_name+'/log_numstat.out.json.bz2'
                try:
                    self.bucket.upload_file(self.numstat_dir, key)
                except Exception as e:
                    print('Error encountered calling S3.Bucket.upload_file: ', key, e)
            else:
                print('Repo Analyzer unable to find local copy of repo directory: ', self.numstat_dir)
                return

            self.parse_json()  # populates analysis_map

            repo_blame_map = {}
            self.repo_dependency_map = {}
            future_blame_result_map = {}
            future_dependency_result_map = {}
            if os.path.exists(self.repo_dir) and self.expire_time > time():
                with ThreadPoolExecutor(max_workers=self.max_threads, thread_name_prefix="CHILDOF_repoAnalyzerThread_") as exec:
                    for subdir, dirs, files in os.walk(self.repo_dir):
                        for file in files:
                            if self.expire_time < time():
                                print('Repo Analyzer process interrupted, terminating thread pool')
                                return
                            filename = os.path.join(subdir, file)
                            relative_file_name = filename[len(self.repo_dir)+1:].replace(os.sep, '/')
                            extension = os.path.splitext(filename)[1].lower()
                            # print('Processing: ', filename, extension)
                            for dep in self.dependency_list:
                                if dep.matches(extension):
                                    # First try and define the blame map - catching any errors
                                    try:
                                        self.blame_game_retriever = BlameGameRetriever(self.repo_dir)
                                        future_blame_result_map[relative_file_name] = \
                                            exec.submit(self.blame_game_retriever.get_blame_game, filename)
                                    except Exception as e:
                                        print(e)
                                        traceback.print_exc()
                                        print('Error encountered calling BlameGameRetriever.get_blame_game: ', filename)
                                    # Now take a similar approach to dependency analysis
                                    try:
                                        future_dependency_result_map[relative_file_name] = \
                                            exec.submit(dep.get_dependencies, filename)
                                    except Exception as e:
                                        print(e)
                                        traceback.print_exc()
                                        print('Error encountered calling dependency-discovery method: ', filename, str(dep))
                    for relative_file_name in future_blame_result_map.keys():
                        if self.expire_time < time():
                            print('Repo Analyzer process interrupted, terminating thread pool')
                            return
                        repo_blame_map[relative_file_name] = future_blame_result_map[relative_file_name].result()
                        self.repo_dependency_map[relative_file_name] = \
                            future_dependency_result_map[relative_file_name].result()
                    self.success = True
                try:
                    # first try and write the blame map to S3
                    if len(repo_blame_map) > 0:
                        blame_map_json = json.dumps(repo_blame_map, ensure_ascii=False)
                        blame_map_zip = bz2.compress(blame_map_json.encode('utf-8'))
                        key = 'repo/'+self.repo_owner+'/'+self.repo_name+'/blame_map.json.bz2'
                        self.bucket.upload_fileobj(io.BytesIO(blame_map_zip), key)
                except Exception as e:
                    self.success = False
                    print('Error encountered calling S3.Bucket.upload_file for blame map: ', self.repo_dir, e)

                try:
                    # Now try and do the same with the dependency map
                    if len(self.repo_dependency_map) > 0:
                        dependency_map_json = json.dumps(self.repo_dependency_map, ensure_ascii=False)
                        dependency_map_zip = bz2.compress(dependency_map_json.encode('utf-8'))
                        key = 'repo/'+self.repo_owner+'/'+self.repo_name+'/dependency_map.json.bz2'
                        self.bucket.upload_fileobj(io.BytesIO(dependency_map_zip), key)
                except Exception as e:
                    self.success = False
                    print('Error encountered calling S3.Bucket.upload_file for dependency map: ', self.repo_dir, e)

                # Now build the parameters for the SQL call
                self.prepare_sql_params()
            else:
                print('Unable to locate repo directory: ', self.repo_dir)

        except Exception as e:
            print(e)
            self.success = False


if __name__ == "__main__":
    RepoAnalyzer(web_lock=Lock()).main()
