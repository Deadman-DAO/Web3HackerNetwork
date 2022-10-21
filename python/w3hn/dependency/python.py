import re

from lib.monitor import timeit
from w3hn.dependency.analyzer import DependencyAnalyzer

class PythonDependencyAnalyzer(DependencyAnalyzer):
    def __init__(self):
        pass

    def language(self):
        return "Python"

    def matches(self, path):
        return path.endswith('.py')

    def get_dependencies(self, path):
        dependencies = list()

        # full_source = ""
        with open(path, 'r', errors='ignore') as source:
            for line in source:
                line = re.sub("//.*", "", line)
                deps = re.findall('^(?:from(?:[\s,]+)([\w\.]+)(?:[\s,]+))?import\s+([\w\., ]+?)(?:\s+as\s+\w+)?\s*$', line)
                if len(deps) == 1 and len(deps[0]) == 2:
                    deps = deps[0]
                    if deps[0] == '':
                        dependencies.append(deps[1])
                    elif deps[1] == '':
                        dependencies.append(deps[0])
                    else:
                        if ',' in deps[1]:
                            prefix = deps[0]
                            postfixes = deps[1].split(',')
                            for postfix in postfixes:
                                postfix = postfix.strip()
                                if ' as ' in postfix:
                                    postfix = postfix[slice(0,postfix.index(' as '))]
                                dependencies.append(f'{prefix}.{postfix}')
                        else:
                            concat = '.'.join((deps[0], deps[1]))
                            dependencies.append(concat)

        return dependencies
