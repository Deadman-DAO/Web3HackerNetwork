from lib.repo_cloner import RepoCloner
from lib.repo_numstat_gatherer import RepoNumstatGatherer
from lib.repo_analyzer import RepoAnalyzer
from os import path

class TestRepo:
    def __init__(self, repo_owner='u-root', repo_name='u-root', repo_id=341256):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.repo_id = repo_id
        self.rc = None
        self.rng = None
        self.vag = None
        self.go()

    def clone_it(self):
        self.rc = RepoCloner()
        self.rc.owner = self.repo_owner
        self.rc.repo_name = self.repo_name
        self.rc.repo_id = self.repo_id
        self.rc.clone_it()

    def numstat_it(self):
        self.rng = RepoNumstatGatherer()
        self.rng.repo_id = self.repo_id
        self.rng.owner = self.repo_owner
        self.rng.repo_name = self.repo_name
        self.rng.repo_dir = self.rc.repo_dir
        self.rng.generate_numstats()

    def analyze_it(self):
        self.vag = RepoAnalyzer()
        self.vag.repo_id = self.repo_id
        self.vag.repo_dir = self.rc.repo_dir
        self.vag.repo_owner = self.repo_owner
        self.vag.repo_name = self.repo_name
        self.vag.numstat_dir = self.rng.results_output_file
        self.vag.process_task()

    def go(self):
        self.clone_it()
        self.numstat_it()
        self.analyze_it()


if __name__ == '__main__':
    TestRepo('u-root', 'u-root', 341256)