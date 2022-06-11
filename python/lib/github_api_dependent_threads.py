from MultiprocessManager import MultiprocessManager
from trace_author_commit_history import AuthorCommitHistoryProcessor
from GitHubUserIDFinder import GitHubUserIDFinder
from repository_investigator import Investigator
from repo_contributor_finder import ContributorFinder
from post_mortem_cleanup import PostMortemCleanerUpper


class GithubThreadMgr(MultiprocessManager):
    def get_process_list(self):
        return {'achp ': AuthorCommitHistoryProcessor,
                'ghuif': GitHubUserIDFinder,
                'inv  ': Investigator,
                'contf': ContributorFinder,
                'hack ': PostMortemCleanerUpper}


if __name__ == "__main__":
    GithubThreadMgr().main()
