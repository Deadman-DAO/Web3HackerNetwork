import re
import json
import os
import sys

relative_lib = "../../../../python"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), relative_lib))
from w3hn.dependency.python import PythonDependencyAnalyzer

repos = list()
owner = "apache"
repo_name = "ant"

sample_source_path = os.path.join(os.path.dirname(__file__), "../data")
paths = [
   f'{sample_source_path}/PythonImport.py',
   f'{sample_source_path}/benchmark.py',
]

repo_dict = dict()
repo_dict['owner'] = owner
repo_dict['repo_name'] = repo_name
repo_dict['dependencies'] = dict()
repos.append(repo_dict)

analyzer = PythonDependencyAnalyzer()
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
        deps = analyzer.get_dependencies(path)
        print(f'type: {type(deps)}')
        print(f'len: {len(deps)}')
        for dep in deps:
            print(f'{owner}\t{repo_name}\t{analyzer.language()}\t{path}\t{dep}')

print()

