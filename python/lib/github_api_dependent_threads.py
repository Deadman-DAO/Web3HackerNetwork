from GitHubUserIDFinder import GitHubUserIDFinder
from MultiprocessManager import MultiprocessManager
from python.lib.post_mortem_cleanup import PostMortemCleanerUpper
from repository_investigator import Investigator
from trace_author_commit_history import AuthorCommitHistoryProcessor


class GithubThreadMgr(MultiprocessManager):
    def get_process_list(self):
        return {'achp ': AuthorCommitHistoryProcessor,
                'ghuif': GitHubUserIDFinder,
                'inv  ': Investigator,
                'clean': PostMortemCleanerUpper}


if __name__ == "__main__":
    GithubThreadMgr().main()
