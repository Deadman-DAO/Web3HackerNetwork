import re
import os
import sys
relative_lib = "../.."
sys.path.insert(0, os.path.join(os.path.dirname(__file__), relative_lib))


class GoDependencyAnalyzer:
    def language(self):
        return "Go"

    def matches(self, path):
        return path.endswith('.go')
        
    def get_dependencies(self, path):
        depends = list()

        # capture single-line imports
        # side-effect: remove '//'-style comments
        full_source = ""
        with open(path, 'r') as go_source:
            for go_line in go_source:
                go_line = re.sub("//.*", "", go_line)
                deps = re.findall('import[^\"]*\"([^\"]*)\"', go_line)
                depends.extend(deps)
                full_source += go_line

        # capture multi-line imports
        ptrn = "import[^\(]*\(([^\)]*)\)"
        lines = re.findall(ptrn, full_source, re.DOTALL)
        for line in lines:
            deps = re.findall('[^\"]*\"([^\"]*)\"[^\"]*', line, re.DOTALL)
            depends.extend(deps)

        return list(set(depends))


if __name__ == '__main__':
    file = sys.argv[1] if len(sys.argv) > 1 else '../../../data/samples/source/go/ir.go'
    print(GoDependencyAnalyzer().get_dependencies(file))