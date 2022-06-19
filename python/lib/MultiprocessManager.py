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

    @abstractmethod
    def get_process_list(self):
        pass

    def main(self):
        self.set_signal_handlers()

        dic = self.get_process_list()
        for kick in dic:
            constructor = dic[kick]
            self.subprocesses.append(ChildProcessContainer(constructor(web_lock=self.web_lock,
                                                                       database_lock=None,
                                                                       git_lock=self.git_lock), kick))
        for n in self.subprocesses:
            n.join()


if __name__ == "__main__":
    MultiprocessManager().main()
