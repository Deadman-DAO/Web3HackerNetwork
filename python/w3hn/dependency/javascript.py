import re

from lib.monitor import timeit
from w3hn.dependency.analyzer import DependencyAnalyzer

class JavascriptDependencyAnalyzer(DependencyAnalyzer):
    def __init__(self):
        pass

    def language(self):
        return "Javascript"

    def matches(self, path):
        if path.endswith('.js'): return true
        elif path.endswith('.ts'): return true
        elif path.endswith('.jsx'): return true
        elif path.endswith('.tsx'): return true
        else: return false

    def get_dependencies(self, path):
        dependencies = list()

        require_pattern = 'require\s*\(\s*[\"\']([^\"\']*)[\"\']\s*\)'
        import_pattern = 'import\s*[^\'\"]*[\'\"]([^\'\"]*)[\'\"]'
        with open(path, 'r', errors='ignore') as source:
            for line in source:
                line = re.sub("//.*", "", line[:-1])
                print(line)
                reqs = re.findall(require_pattern, line)
                dependencies.extend(reqs)
                imps = re.findall(import_pattern, line)
                dependencies.extend(imps)
        return dependencies
