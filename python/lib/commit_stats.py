import os
import json

def find_files(name, path):
    result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root, name))
    return result

def parse_commits(commit_files):
    all_logs = []
    all_commits = []
    for file in commit_files:
        in_stats = json.loads(open(file, 'r').read());
        all_logs.append(in_stats)
        for commit in in_stats:
            all_commits.append(commit)
    return all_commits

def load_commit_stats(name, path):
    files = find_files(name, path)
    return parse_commits(files)
