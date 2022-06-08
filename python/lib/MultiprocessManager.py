from threading import Lock
from child_process import ChildProcessContainer
from abc import abstractmethod


class MultiprocessManager:
    def __init__(self):
        self.lock = Lock()
        self.subprocesses = []

    @abstractmethod
    def get_process_list(self):
        pass

    def main(self):
        dic = self.get_process_list()
        for kick in dic:
            constructor = dic[kick]
            self.subprocesses.append(ChildProcessContainer(constructor(self.lock), kick))
        for n in self.subprocesses:
            n.join()


if __name__ == "__main__":
    MultiprocessManager().main()
