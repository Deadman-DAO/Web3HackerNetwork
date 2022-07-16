import bz2
import os
import json
import hashlib
import random
from datetime import datetime

def find_files(name, path):
    # print(str(name) + ", " + str(path))
    result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            # print(str(root) + ", " + str(dirs) + ", " + str(files))
            result.append(os.path.join(root, name))
    return result

def parse_commits(commit_files, stat_file_name):
    all_logs = []
    all_commits = []
    for file in commit_files:
        path_pos = file.find(stat_file_name)
        path_parts = file[:path_pos].split('/')
        first_part = path_parts[len(path_parts) - 3]
        second_part = path_parts[len(path_parts) - 2]
        project = first_part + '/' + second_part
        in_stats = {}
        if stat_file_name.endswith("bz2"):
            try:
                in_stats = json.loads(bz2.open(file).read())
            except:
                next
        else:
            in_stats = json.loads(open(file, 'r').read())
        all_logs.append(in_stats)
        for commit in in_stats:
            commit['seen_in'] = [project]
            
            author = commit['Author']
            author_hash = hashlib.md5(bytes(author, 'utf-8')).hexdigest()
            commit['author_hash'] = author_hash
            
            dtstring = commit['Date']
            # dtform = 'Date:    %a %b %d %H:%M:%S %Y %z'
            # dt = datetime.strptime(dtstring, dtform)
            dt = datetime.fromisoformat(dtstring)
            iso_datetime = dt.isoformat()
            utc_datetime = datetime.utcfromtimestamp(dt.timestamp()).isoformat()
            commit['iso_datetime'] = iso_datetime
            commit['utc_datetime'] = utc_datetime
            
            all_commits.append(commit)
    return all_commits

def load_commit_stats(stat_file_name, path, start=0, quant=0):
    random.seed(1)
    files = find_files(stat_file_name, path)
    random.shuffle(files)
    random.seed()
    if (start >= 0 and quant > 0):
        if (start + quant) > len(files):
            quant = len(files) - start
        files = files[slice(start, start+quant)]
    return parse_commits(files, stat_file_name)
