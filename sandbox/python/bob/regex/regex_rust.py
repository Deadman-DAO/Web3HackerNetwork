import re

class RustDependencyAnalyzer:
    def language(self):
        return "Rust"

    def matches(self, path):
        return path.endswith('.rs')

    def get_dependencies(self, path):
        dependencies = list()

        # full_source = ""
        source = open(path, 'r')
        for line in source:
            line = re.sub("//.*", "", line)
            deps = re.findall('use[\s]+(?!crate::)(.*)', line)
            dependencies.extend(deps)
            # full_source += line
        
        return dependencies
