import multiprocessing
from abc import abstractmethod
from threading import Lock

from child_process import ChildProcessContainer
from signal_handler import SignalHandler


class MultiprocessManager(SignalHandler):

    def __init__(self):
        self.web_lock = Lock()
        self.db_lock = Lock()
        self.git_lock = Lock()
        self.subprocesses = []
        self.cpu_count = multiprocessing.cpu_count()

    @abstractmethod
    def get_process_list(self):
        pass

    def get_web_lock(self):
        return self.web_lock

    def get_db_lock(self):
        return None

    def get_git_lock(self):
        return self.git_lock if self.cpu_count < 2 else Lock()

    def main(self):
        self.set_signal_handlers()

        dic = self.get_process_list()
        for kick in dic:
            constructor = dic[kick]
            self.subprocesses.append(ChildProcessContainer(constructor(web_lock=self.get_web_lock(),
                                                                       database_lock=get_db_lock(),
                                                                       git_lock=self.get_git_lock()), kick))
        for n in self.subprocesses:
            n.join()


if __name__ == "__main__":
    MultiprocessManager().main()
