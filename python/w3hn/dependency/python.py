import re
import os
import sys
relative_lib = "../.."
sys.path.insert(0, os.path.join(os.path.dirname(__file__), relative_lib))

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
        with open(path, 'r', errors='ignore') as source:
            for line in source:
                line = re.sub("//.*", "", line)
                deps = re.findall('^(?:from(?:[\s,]+)([\w\.]+)(?:[\s,]+))?import\s+([\w, ]+)(?:\s+as\s+\w+)?\s*$', line)
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


if __name__ == '__main__':
    file = sys.argv[1] if len(sys.argv) > 1 else '../../../data/samples/source/python/plugin.py'
    print(PythonDependencyAnalyzer().get_dependencies(file))