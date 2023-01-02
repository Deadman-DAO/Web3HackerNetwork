import os
from pathlib import Path
from shutil import rmtree
from threading import Lock

from lib.db_driven_task import DBDrivenTaskProcessor, DBTask
from lib.monitor import timeit


class RepoCleanup(DBDrivenTaskProcessor):

    def init(self):
        pass

    class Fetcher(DBTask):
        def __init__(self, mom):
            self.mom = mom

        def get_proc_name(self):
            return 'ReserveNextRepoForCleanup'

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
            return result

    class Closer(DBTask):
        def __init__(self, mom):
            self.mom = mom

        def get_proc_name(self):
            return 'ReleaseRepoAfterCleanup_v01'

        def get_proc_parameters(self):
            return [self.mom.repo_id]

        def process_db_results(self, result_args):
            pass

    def __init__(self, **kwargs):
        DBDrivenTaskProcessor.__init__(self, **kwargs)
        self.repo_id = None
        self.repo_owner = None
        self.repo_name = None
        self.repo_dir = None
        self.fetcher = self.Fetcher(self)
        self.closer = self.Closer(self)

    def get_job_fetching_task(self):
        return self.fetcher

    def get_job_completion_task(self):
        return self.closer

    @timeit
    def process_task(self):
        target_dir = ['./repos/'+self.repo_owner+'/'+self.repo_name, './results/'+self.repo_owner+'/'+self.repo_name]
        for dir in target_dir:
            if os.path.isdir(dir):
                rmtree(dir, ignore_errors=True)
                rmtree(Path(dir).parent, ignore_errors=True)


if __name__ == "__main__":
    RepoCleanup(web_lock=Lock()).main()
