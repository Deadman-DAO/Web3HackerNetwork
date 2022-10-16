import re
import json
import sys

sys.path.append("../../../../python/lib")
from regex_java import JavaDependencyAnalyzer

repos = list()
owner = "apache"
repo_name = "ant"
paths = [
    '../data/JavaImport.java',
]
repo_dict = dict()
repo_dict['owner'] = owner
repo_dict['repo_name'] = repo_name
repo_dict['dependencies'] = dict()
repos.append(repo_dict)

analyzer = JavaDependencyAnalyzer()
for path in paths:
    if (analyzer.matches(path)):
        dependencies = analyzer.get_dependencies(path)
        if analyzer.language() not in repo_dict['dependencies']:
            repo_dict['dependencies'][analyzer.language()] = list()
        dep_dict = dict()
        dep_dict['file_path'] = path
        dep_dict['dependencies'] = dependencies
        repo_dict['dependencies'][analyzer.language()].append(dep_dict)

print()
print("Target JSON Data Form")
print(json.dumps(repos, indent=2))

print()
print("Target Raw Data Form")
print('owner\trepo_name\tlanguage\tfile_path\tdependency')
for path in paths:
    if analyzer.matches(path):
        for dep in analyzer.get_dependencies(path):
            print(f'{owner}\t{repo_name}\t{analyzer.language()}\t{path}\t{dep}')

print()

