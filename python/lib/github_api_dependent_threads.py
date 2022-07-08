from GitHubUserIDFinder import GitHubUserIDFinder
from MultiprocessManager import MultiprocessManager
from repository_investigator import Investigator
from trace_author_commit_history import AuthorCommitHistoryProcessor


class GithubThreadMgr(MultiprocessManager):
    def get_process_list(self):
        return {'achp ': AuthorCommitHistoryProcessor,
                'ghuif': GitHubUserIDFinder,
                'inv  ': Investigator}


if __name__ == "__main__":
    GithubThreadMgr().main()
