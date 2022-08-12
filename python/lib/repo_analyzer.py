import ast
import base64
import bz2
import hashlib
import json
import os
import traceback
from abc import ABC, abstractmethod
from threading import Lock
from db_driven_task import DBDrivenTaskProcessor, DBTask
from monitor import timeit


def add_to_map(map, key, value):
    if key not in map:
        map[key] = 0
    map[key] += value


class Analyzer(ABC):
    @abstractmethod
    def analyze(self, numstat_json, extension_map, filename_map, repo_dir, import_map):
        pass


class PythonAnalyzer(Analyzer):

    def get_imports(self, obj, import_map):
        for node in ast.walk(obj):
            if isinstance(node, ast.Module):
                for b in node.body:
                    if isinstance(b, ast.Import):
                        for i in b.names:
                            add_to_map(import_map, i.name, 1)
                            if '.' in i.name:
                                add_to_map(import_map, i.name.split('.')[0], 1)
                    if isinstance(b, ast.ImportFrom):
                        add_to_map(import_map, b.module, 1)
                        for n in b.names:
                            if b.module and n and n.name:
                                add_to_map(import_map, b.module+'.'+n.name, 1)
                            else:
                                print("Null value found within PythonAnalyzer import mapping: ", b.module, n.name);
                        if '.' in b.module:
                            add_to_map(import_map, b.module.split('.')[0], 1)

    def analyze(self, numstat_json, extension_map, filename_map, repo_dir, import_map):
        if 'py' in extension_map and extension_map['py'] > 0:
            for filename in filename_map:
                if filename.endswith('.py'):
                    if os.path.exists(os.path.join(repo_dir, filename)):
                        try:
                            with open(os.path.join(repo_dir, filename), 'r') as f:
                                contents = f.read()
                                obj = ast.parse(contents, filename=filename)
                                self.get_imports(obj, import_map)
                        except Exception as e:
                            print('Non-compilable (or pre-Python3) python code:', e)


class RepoAnalyzer(DBDrivenTaskProcessor):
    def __init__(self, **kwargs):
        DBDrivenTaskProcessor.__init__(self, **kwargs)
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
        self.hacker_name_map = {}
        self.stats_json = None

    def init(self):
        pass

    class GetNextRepoForAnalysis(DBTask):
        def __init__(self, mom):
            self.mom = mom

        def get_proc_name(self):
            return 'ReserveNextRepoForAnalysis'

        def get_proc_parameters(self):
            return [self.mom.machine_name]

        def process_db_results(self, result_args):
            for goodness in self.mom.cursor.stored_results():
                result = goodness.fetchone()
                if result:
                    self.mom.repo_id = int(result[0])
                    self.mom.repo_owner = result[1]
                    self.mom.repo_name = result[2]
                    self.mom.repo_dir = result[3]
                    self.mom.numstat_dir = result[4]
            return result

    class ReleaseRepo(DBTask):
        def __init__(self, mom):
            self.mom = mom

        def get_proc_name(self):
            return 'ReleaseRepoFromAnalysis'

        def get_proc_parameters(self):
            return [self.mom.repo_id, self.mom.numstat, self.mom.success, self.mom.stats_json]

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
        self.hacker_name_map = {}
        for commit in self.numstat_json:
            author = commit['Author']
            try:
                author_md5 = hashlib.md5(author.encode('utf-8')).hexdigest()
            except Exception as e:
                print(e)
                b = bytearray(author, 'unicode-escape')
                author_md5 = hashlib.md5(b).hexdigest()
            if author_md5 not in self.hacker_extension_map:
                self.hacker_extension_map[author_md5] = {}
                self.hacker_name_map[author_md5] = author
            for key, val in commit['fileTypes'].items():
                add_to_map(self.extension_map, key, val['occurrences'])
                add_to_map(self.hacker_extension_map[author_md5], key, val['occurrences'])
            for key, val in commit['file_list'].items():
                add_to_map(self.filename_map, key, 1)

    @timeit
    def prepare_sql_params(self):
        print('Preparing sql params')
        try:
            self.stats_json = {'hacker_extension_map': self.hacker_extension_map,
                               'hacker_name_map': self.hacker_name_map,
                               'extension_map': self.extension_map,
                               'import_map_map': self.import_map_map}
            self.stats_json = json.dumps(self.stats_json, ensure_ascii=False)
        finally:
            print('Exiting prepare_sql_params')

    @timeit
    def process_task(self):
        try:
            if os.path.exists(self.numstat_dir):
                self.extension_map = {}
                self.hacker_name_map = {}
                self.hacker_extension_map = {}
                self.import_map_map = {}
                with open(self.numstat_dir, 'rb') as r:
                    self.numstat_raw = r.read()

                self.numstat = base64.b64encode(self.numstat_raw)
                self.parse_json()
                for ext, analysis in self.analysis_map.items():
                    self.import_map_map[ext] = {}
                    analysis.analyze(self.numstat_json, self.extension_map,
                                     self.filename_map, self.repo_dir, self.import_map_map[ext])
                self.prepare_sql_params()

        except Exception as e:
            print(e)


if __name__ == "__main__":
    RepoAnalyzer(web_lock=Lock()).main()
