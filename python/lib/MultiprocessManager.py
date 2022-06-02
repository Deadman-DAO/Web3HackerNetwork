import time
from trace_author_commit_history import AuthorCommitHistoryProcessor
from monitor import MultiprocessMonitor
from monitor import timeit
from GitHubUserIDFinder import GitHubUserIDFinder
from repository_investigator import Investigator
from repository_investigator import ContributorFinder
from threading import Thread, Lock
from child_process import ChildProcessContainer


class TestClass:
    def __init__(self, lock):
        self.lock = lock
        self.monitor = MultiprocessMonitor(lock, friend=self.is_running)
        self.running = True

    def is_running(self):
        return self.running

    @timeit
    def main(self):
        time.sleep(30)
        print('Attempting to block')
        self.lock.acquire()
        print('Blocking!')
        time.sleep(30)
        self.lock.release()
        print('Okay.  No more blockage')
        self.running = False


class MultiprocessManager:
    def __init__(self):
        self.lock = Lock()
        self.subprocesses = []

    def main(self):
        self.subprocesses.append(ChildProcessContainer(AuthorCommitHistoryProcessor(self.lock), 'achp'))
        self.subprocesses.append(ChildProcessContainer(GitHubUserIDFinder(self.lock), 'ghuif'))
        self.subprocesses.append(ChildProcessContainer(Investigator(self.lock), 'inv'))
        self.subprocesses.append(ChildProcessContainer(ContributorFinder(self.lock), 'contf'))
        for n in self.subprocesses:
            n.join()


if __name__ == "__main__":
    MultiprocessManager().main()
