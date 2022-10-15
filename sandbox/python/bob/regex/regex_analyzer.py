import sys
sys.path.append("/home/bob/projects/Web3HackerNetwork/python/lib/")
from repo_analyzer import PythonAnalyzer

import json

repo_dir = "/home/bob/projects/Web3HackerNetwork/sandbox/data/bob/repos-2022-05-24/pypa/manylinux/"
numstat_path = repo_dir + "commit_stat_log.json"
numstat_json = json.loads(open(numstat_path, 'r').read());
extension_map = {"py": 1}
filename_map = {}
import_map = {"contributors": {}}
commit_to_hacker_map = {}

import os

base_dir = "/home/bob/projects/Web3HackerNetwork"
repo_dir = os.path.join(base_dir, "sandbox/data/bob/repos-2022-05-24/tmp/numpy/numpy")

def recurse_dir(path, relative_path, file_list):
    for entry in os.scandir(path):
        if entry.is_dir():
            new_path = os.path.join(path, entry.name)
            new_relative_path = os.path.join(relative_path, entry.name)
            recurse_dir(new_path, new_relative_path, file_list)
        elif entry.is_file():
            if entry.name.endswith(".py"):
                file_path = os.path.join(relative_path, entry.name)
                file_list.append(file_path)

file_list = []
recurse_dir(repo_dir, '', file_list)
print(file_list[slice(0,5)])

filename_map = {}
for file in file_list:
    filename_map[file] = 1

#


lyza = PythonAnalyzer()
lyza.analyze(numstat_json, extension_map, filename_map, repo_dir,
              import_map, commit_to_hacker_map)

print(import_map)
