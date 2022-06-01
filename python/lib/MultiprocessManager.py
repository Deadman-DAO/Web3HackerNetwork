from multiprocessing import Process, Lock
import time
from trace_author_commit_history import AuthorCommitHistoryProcessor
from monitor import MultiprocessMonitor
from monitor import timeit
from GitHubUserIDFinder import GitHubUserIDFinder
from repository_investigator import Investigator


class ChildProcessContainer(Process):
    def __init__(self, managed_instance):
        super().__init__(target=self.run, daemon=False)
        self.managed_instance = managed_instance
        self.start()

    def run(self):
        self.managed_instance.main()


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
        self.subprocesses.append(ChildProcessContainer(AuthorCommitHistoryProcessor(self.lock)))
        self.subprocesses.append(ChildProcessContainer(GitHubUserIDFinder(self.lock)))
        self.subprocesses.append(ChildProcessContainer(Investigator(self.lock)))
        for n in self.subprocesses:
            n.join()


if __name__ == "__main__":
    MultiprocessManager().main()
