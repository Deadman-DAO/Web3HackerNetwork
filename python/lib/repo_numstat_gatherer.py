from db_dependent_class import DBDependent, make_dir
from monitor import MultiprocessMonitor, timeit

class RepoNumstatGatherer(DBDependent):
    def __init__(self, lock):
        DBDependent.__init__(self)
        self.lock = lock
        self.monitor = MultiprocessMonitor(lock)
        self.result_base_dir = './results'
        make_dir(self.result_base_dir)

