from MultiprocessManager import MultiprocessManager
from trace_author_commit_history import AuthorCommitHistoryProcessor
from GitHubUserIDFinder import GitHubUserIDFinder
from repository_investigator import Investigator
from repo_contributor_finder import ContributorFinder


class GithubThreadMgr(MultiprocessManager):
    def get_process_list(self):
        return {'achp ': AuthorCommitHistoryProcessor,
                'ghuif': GitHubUserIDFinder,
                'inv  ': Investigator,
                'contf': ContributorFinder}


if __name__ == "__main__":
    GithubThreadMgr().main()
