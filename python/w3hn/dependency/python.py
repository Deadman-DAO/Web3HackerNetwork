import re


class PythonDependencyAnalyzer:
    def __init__(self):
        pass

    def language(self):
        return "Python"

    def matches(self, path):
        return path.endswith('.py')

    def get_dependencies(self, path):
        dependencies = list()

        # full_source = ""
        with open(path, 'r') as source:
            for line in source:
                line = re.sub("//.*", "", line)
                deps = re.findall('^(?:from(?:[\s,]+)([\w\.]+)(?:[\s,]+))?import\s+(\w+)(?:\s+as\s+\w+)?\s*$', line)
                if len(deps) == 1 and len(deps[0]) == 2:
                    deps = deps[0]
                    if deps[0] == '':
                        deps = deps[1]
                    elif deps[1] == '':
                        deps = deps[0]
                    else:
                        deps = '.'.join((deps[0], deps[1]))
                    dependencies.append(deps)

        return dependencies
