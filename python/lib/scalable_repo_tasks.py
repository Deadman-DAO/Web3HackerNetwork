from MultiprocessManager import MultiprocessManager
from repo_analyzer import RepoAnalyzer
from repo_cleaner import RepoCleanup
from repo_cloner import RepoCloner;
from repo_numstat_gatherer import RepoNumstatGatherer
import faulthandler
import signal


class ScalableRepoTasks(MultiprocessManager):
    def __init__(self):
        MultiprocessManager.__init__(self)
        faulthandler.register(signal.SIGUSR1)

    def get_process_list(self):
        return {'clone': RepoCloner,
                'nmst': RepoNumstatGatherer,
                'vaj ': RepoAnalyzer,
                'clnr': RepoCleanup}


if __name__ == '__main__':
    ScalableRepoTasks().main()
