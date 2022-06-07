from MultiprocessManager import MultiprocessManager
from repo_cloner import RepoCloner;
from repo_analyzer import RepoAnalyzer
from repo_numstat_gatherer import RepoNumstatGatherer
from repo_cleaner import RepoCleanup


class ScalabelRepoTasks(MultiprocessManager):
    def get_process_list(self):
        return {'clone': RepoCloner,
                'nmst': RepoNumstatGatherer,
                'vaj ': RepoAnalyzer,
                'clnr': RepoCleanup}


if __name__ == '__main__':
    ScalabelRepoTasks().main()
