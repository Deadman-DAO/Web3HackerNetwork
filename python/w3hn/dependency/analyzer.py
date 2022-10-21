from abc import ABC, abstractmethod
from lib.monitor import timeit

class DependencyAnalyzer(ABC):
    @abstractmethod
    @timeit
    def language(self):
        pass
    @abstractmethod
    @timeit
    def matches(self, path):
        pass
    @abstractmethod
    @timeit
    def get_dependencies(self, path):
        pass
