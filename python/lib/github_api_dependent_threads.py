from lib.GitHubUserIDFinder import GitHubUserIDFinder
from lib.MultiprocessManager import MultiprocessManager
from lib.repository_investigator import Investigator
from lib.trace_author_commit_history import AuthorCommitHistoryProcessor


class GithubThreadMgr(MultiprocessManager):
    def get_process_list(self):
        return {'achp ': AuthorCommitHistoryProcessor,
                'ghuif': GitHubUserIDFinder,
                'inv  ': Investigator}


if __name__ == "__main__":
    GithubThreadMgr().main()
