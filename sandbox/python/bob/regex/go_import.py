import re
import json

owner = "apache"
repo_name = "ant"
paths = [
    '../data/go_import.go',
    '../data/other_go_import.go',
]
repo_dict = dict()
repo_dict['owner'] = owner
repo_dict['repo_name'] = repo_name
repo_dict['dependencies'] = dict()

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
        go_source = open(path, 'r')
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

analyzer = GoDependencyAnalyzer()
for path in paths:
    if (analyzer.matches(path)):
        dependencies = analyzer.get_dependencies(path)
        if analyzer.language() not in repo_dict['dependencies']:
            repo_dict['dependencies'][analyzer.language()] = list()
        dep_dict = dict()
        dep_dict['file_path'] = path
        # dep_dict['language'] = analyzer.language()
        dep_dict['dependencies'] = dependencies
        repo_dict['dependencies'][analyzer.language()].append(dep_dict)

print()
print("Target JSON Data Form")
print(json.dumps(repo_dict, indent=2))

print()
print("Target Raw Data Form")
print('owner\trepo_name\tlanguage\tfile_path\tdependency')
for path in paths:
    if analyzer.matches(path):
        for dep in analyzer.get_dependencies(path):
            print(f'{owner}\t{repo_name}\t{analyzer.language()}\t{path}\t{dep}')

print()

