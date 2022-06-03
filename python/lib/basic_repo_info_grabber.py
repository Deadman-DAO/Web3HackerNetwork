from db_dependent_class import DBDependent
from git_hub_client import GitHubClient


class RepoGrabber(DBDependent, GitHubClient):
    def __init__(self, lock):
        RepoGrabber.__init__(self)
        GitHubClient.__init__(self, lock)
