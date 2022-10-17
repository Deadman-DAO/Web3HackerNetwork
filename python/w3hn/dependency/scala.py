import re

class ScalaDependencyAnalyzer:
    def language(self):
        return "Scala"

    def matches(self, path):
        return path.endswith('.scala')

    def get_dependencies(self, path):
        dependencies = list()

        # full_source = ""
        with open(path, 'r') as source:
            for line in source:
                line = re.sub("//.*", "", line)
                deps = re.findall('import[\s]+(?:static[\s]+)?([^ {]*)', line)
                dependencies.extend(deps)
                # full_source += line
        
        return dependencies
