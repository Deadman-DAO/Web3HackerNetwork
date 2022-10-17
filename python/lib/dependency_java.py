import re

class JavaDependencyAnalyzer:
    def language(self):
        return "Java"

    def matches(self, path):
        return path.endswith('.java')

    def get_dependencies(self, path):
        dependencies = list()

        # full_source = ""
        source = open(path, 'r')
        for line in source:
            line = re.sub("//.*", "", line)
            deps = re.findall('import[\s]+(?:static[\s]+)?([^;]*);', line)
            dependencies.extend(deps)
            # full_source += line
        
        return dependencies
