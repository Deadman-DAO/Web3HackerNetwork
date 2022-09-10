import boto3
import ast
import base64
import bz2
import hashlib
import json
import os
import sys
import traceback
from abc import ABC, abstractmethod
from threading import Lock
from db_driven_task import DBDrivenTaskProcessor, DBTask
from monitor import timeit
from signal_handler import SignalHandler
from datetime import datetime as datingdays



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


class Analyzer(ABC):
    @abstractmethod
    def analyze(self, numstat_json, extension_map, filename_map, repo_dir, import_map_map, commit_to_hacker_map):
        pass


class PythonAnalyzer(Analyzer):

    def add_import(self, import_map, import_name, contributor_hash):
        if import_name not in import_map:
            import_map[import_name] = []
        been_there = False
        for h in import_map[import_name]:
            if h == contributor_hash:
                been_there = True
                break
        if not been_there:
            import_map[import_name].append(contributor_hash)
            if '.' in import_name:
                self.add_import(import_map, import_name.split('.')[0], contributor_hash)

    def get_imports(self, obj, import_map, contributor_hash, filename=None, repo_dir=None):
        for node in ast.walk(obj):
            if isinstance(node, ast.Module):
                for b in node.body:
                    if isinstance(b, ast.Import):
                        for i in b.names:
                            self.add_import(import_map, i.name, contributor_hash)
                    if isinstance(b, ast.ImportFrom):
                        for n in b.names:
                            if b.module and n and n.name:
                                self.add_import(import_map, b.module + '.' + n.name, contributor_hash)
                            else:
                                print("Null value found within PythonAnalyzer import mapping: ", filename, ':', b.module, n.name, b.lineno, repo_dir)

    def analyze(self, numstat_json, extension_map, filename_map, repo_dir,
                import_map, commit_to_hacker_map):
        if 'py' in extension_map and extension_map['py'] > 0:
            bg = BlameGameRetriever(repo_dir, commit_to_hacker_map)
            for filename in filename_map:
                if filename.endswith('.py'):
                    qualified_filename = os.path.join(repo_dir, filename)
                    if os.path.exists(qualified_filename):
                        try:
                            with open(qualified_filename, 'r') as f:
                                contents = f.read()

                            if contents:
                                hacker_contribution_map = bg.get_blame_game(filename)
                                md5key = hashlib.md5(''.join((filename, json.dumps(hacker_contribution_map))).
                                                     encode('utf-8')).hexdigest()
                                try:
                                    obj = ast.parse(contents, filename=filename)
                                    if 'contributors' not in import_map:
                                        import_map['contributors'] = {}
                                    import_map['contributors'][md5key] = hacker_contribution_map
                                    if 'imports' not in import_map:
                                        import_map['imports'] = {}

                                    self.get_imports(obj, import_map['imports'], md5key,
                                                     filename=filename, repo_dir=repo_dir)
                                except Exception as e:
                                    print("Python source file didn't compile: ", filename, e)
                                    traceback.print_exc()
                                    continue
                        except Exception as e:
                            print('Non-compilable (or pre-Python3) python code:', e)
                            traceback.print_exc()


class BlameGameRetriever(SignalHandler):
    def __init__(self, repo_dir, commit_author_map):
        SignalHandler().__init__()
        self.repo_dir = repo_dir
        self.success = False
        self.stdout = None
        self.stderr = None
        self.commit_author_map = commit_author_map
        self.max_wait = 60

    def get_blame_game(self, filename) -> dict:
        hacker_contribution_map = {}
        full_name = os.path.join(self.repo_dir, filename)
        if not os.path.exists(full_name):
            return None
        cmd = ['nice',  'git', '-C', self.repo_dir, 'blame', '-l', filename]

        if sys.platform == "win32":
            # Take out the first element of the cmd array as windows isn't "nice"
            cmd = cmd[1:]
        self.success, self.stdout, self.stderr = self.execute_os_cmd(cmd)
        if self.success is not None and self.success is True and self.stdout is not None:
            line_count = 0.0
            self.stdout = self.stdout.decode('utf-8')
            for line in self.stdout.split('\n'):
                words = line.split(' ')
                if len(words) > 0 and len(words[0]) == 40:
                    line_count += 1
                    who_when_line = line[42:].split(')')[0]
                    items = who_when_line.split(' ')
                    if len(items) > 4:
                        line = int(items[len(items) - 1])
                        if words[0] in self.commit_author_map:
                            # commit hash found in commit_author_map
                            # retrieving author's md5sum
                            author_hash = self.commit_author_map[words[0]]
                            if author_hash not in hacker_contribution_map:
                                hacker_contribution_map[author_hash] = 0
                            hacker_contribution_map[author_hash] += 1
            for key in hacker_contribution_map:
                hacker_contribution_map[key] = hacker_contribution_map[key] / (line_count if line_count > 0 else 1.0)
            return hacker_contribution_map

'''
ae0f28169a3da4300d6bf66a24fcfb9d6ff9df86 (enigmatt 2022-06-11 13:03:16 -0700 188)     RepoAnalyzer(web_lock=Lock()).main()
1234567890123456789012345678901234567890
'''


class RepoAnalyzer(DBDrivenTaskProcessor):
    def __init__(self, **kwargs):
        DBDrivenTaskProcessor.__init__(self, **kwargs)
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
        self.analysis_map = {'py': PythonAnalyzer()}
        self.import_map_map = {}
        self.hacker_extension_map = {}
        self.hacker_md5_map = None
        self.stats_json = None
        self.cur_job = 'Starting...'
        self.find_orphan_sql = None
        self.hacker_name_map = None
        self.s3r = boto3.resource('s3')
        self.bucket = self.s3r.Bucket('numstat-bucket')

    def init(self):
        pass

    class GetNextRepoForAnalysis(DBTask):
        def __init__(self, mom):
            self.mom = mom

        def get_proc_name(self):
            return 'ReserveNextRepoForAnalysis'

        def get_proc_parameters(self):
            print(datingdays.now().isoformat(), 'Calling ReserveNextRepoForAnalysis', 'b47455b4a84eb638a33864dc466abc6f')
            return [self.mom.machine_name]

        def process_db_results(self, result_args):
            result = None
            for goodness in self.mom.cursor.stored_results():
                result = goodness.fetchone()
                if result:
                    self.mom.repo_id = int(result[0])
                    self.mom.repo_owner = result[1]
                    self.mom.repo_name = result[2]
                    self.mom.repo_dir = result[3]
                    self.mom.numstat_dir = result[4]
                    self.mom.cur_job = result[1] + ':' + result[2]
            print(datingdays.now().isoformat(), 'Returned from ReserveNextRepoForAnalysis', self.mom.repo_id, 'b47455b4a84eb638a33864dc466abc6f')
            if result is None:
                self.mom.cur_job = 'Nada'
            return result

    class ReleaseRepo(DBTask):
        def __init__(self, mom):
            self.mom = mom

        def get_proc_name(self):
            return 'ReleaseRepoFromAnalysis'

        def get_proc_parameters(self):
            print(datingdays.now().isoformat(), 'Calling ReleaseRepoFromAnalysis', self.mom.repo_id)
            return [self.mom.repo_id, self.mom.success, self.mom.stats_json]

        def process_db_results(self, result_args):
            return True

    def get_job_fetching_task(self):
        return self.get_next

    def get_job_completion_task(self):
        return self.all_done

    @timeit
    def parse_json(self):
        self.numstat_str = bz2.decompress(self.numstat_raw)
        self.numstat_json = json.loads(self.numstat_str)
        self.extension_map = {}
        self.filename_map = {}
        self.hacker_extension_map = {}
        self.hacker_md5_map = {}
        self.hacker_name_map = {}
        self.commit_to_hacker_map = {}
        for commit in self.numstat_json:
            author = commit['Author']
            try:
                author_md5 = hashlib.md5(author.encode('utf-8')).hexdigest()
            except Exception as e:
                print(e)
                traceback.print_exc()
                b = bytearray(author, 'unicode-escape')
                author_md5 = hashlib.md5(b).hexdigest()
            if author_md5 not in self.hacker_extension_map:
                self.hacker_extension_map[author_md5] = {}
                self.hacker_md5_map[author_md5] = author
                self.hacker_name_map[author_md5] = author
            commit_id = commit['commit']
            if commit_id not in self.commit_to_hacker_map:
                self.commit_to_hacker_map[commit_id] = author_md5  # Are there ever more than one author per commit?
            for key, val in commit['fileTypes'].items():
                add_int_to_map(self.extension_map, key, val['occurrences'])
                add_int_to_map(self.hacker_extension_map[author_md5], key, val['occurrences'])
            for key, val in commit['file_list'].items():
                add_int_to_map(self.filename_map, key, 1)

    @timeit
    def prepare_sql_params(self):
        self.stats_json = {'hacker_extension_map': self.hacker_extension_map,
                           'hacker_name_map': self.hacker_name_map,
                           'extension_map': self.extension_map,
                           'import_map_map': self.import_map_map}
        self.stats_json = json.dumps(self.stats_json, ensure_ascii=False)

    @timeit
    def process_task(self):
        try:
            if os.path.exists(self.numstat_dir):
                self.extension_map = {}
                self.hacker_md5_map = {}
                self.hacker_extension_map = {}
                self.import_map_map = {}
                with open(self.numstat_dir, 'rb') as r:
                    self.numstat_raw = r.read()
                key = 'repo/'+self.mom.repo_owner+'/'+self.mom.repo_name+'/log_numstat.out.json.bz2'
                try:
                    self.mom.bucket.upload_file(self.mom.numstat_dir, key)
                except Exception as e:
                    print('Error encountered calling S3.Bucket.upload_file: ', key, e)

                self.numstat = base64.b64encode(self.numstat_raw)
                self.parse_json()
                for ext, analysis in self.analysis_map.items():
                    self.import_map_map[ext] = {}
                    analysis.analyze(self.numstat_json,           # Numstat in browsable JSON format
                                     self.extension_map,          # Extension -> count map
                                     self.filename_map,           # Filename -> count map
                                     self.repo_dir,               # Repo directory
                                     self.import_map_map[ext],    # New Import map for this extension
                                                                  # - analyze will add to this map
                                     self.commit_to_hacker_map)   # Author lookup map via commit ID (for BlameGame)
                                                                  # - provided by parse_json()
                self.prepare_sql_params()

        except Exception as e:
            print(e)
            traceback.print_exc()



if __name__ == "__main__":
    RepoAnalyzer(web_lock=Lock()).main()
