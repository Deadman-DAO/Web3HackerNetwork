import bz2
import json

owner = 'apache'
repo_name = 'ant'
repo_path = '../../data/bob/numstat/'+owner+'/'+repo_name
numstat_path = repo_path+'/log_numstat.out.json.bz2'
numstat_raw = ''
with open(numstat_path, 'rb') as r:
    numstat_raw = r.read()

numstat_str = bz2.decompress(numstat_raw)
numstat_object = json.loads(numstat_str)

def do_things(owner, repo_name, numstat_object, repo_path):
    project_files = dict()
    for commit in numstat_object:
        #print(commit)
        for file_path in commit['file_list']:
            file_entry = commit['file_list'][file_path]
            if file_path in project_files:
                file_metadata = project_files[file_path]
                file_metadata['num_commits'] += 1
                if commit['Date'] < file_metadata['first_commit_date']:
                    file_metadata['last_commit_date'] = commit['Date']
                if commit['Date'] > file_metadata['last_commit_date']:
                    file_metadata['last_commit_date'] = commit['Date']
                file_metadata['total_inserts'] += file_entry['inserts']
                file_metadata['total_deletes'] += file_entry['deletes']
            else:
                file_metadata = dict()
                file_metadata['num_commits'] = 1
                file_metadata['first_commit_date'] = commit['Date']
                file_metadata['last_commit_date'] = commit['Date']
                file_metadata['total_inserts'] = file_entry['inserts']
                file_metadata['total_deletes'] = file_entry['deletes']
                file_metadata['binary'] = file_entry['binary']
                project_files[file_path] = file_metadata
    unique_files = list(project_files.keys())
    unique_files.sort()
    #print(unique_files)
    # print("owner\trepo_name\tfile_path\tnum_commits"
    #       +"\tfirst_commit_date\tlast_commit_date"
    #       +"\ttotal_inserts\ttotal_deletes\tbinary")
    # for file_path in unique_files:
    #     meta = project_files[file_path]
    #     print(owner+"\t"+repo_name+"\t"+file_path
    #           +"\t"+str(meta['num_commits'])
    #           +"\t"+str(meta['first_commit_date'])
    #           +"\t"+str(meta['last_commit_date'])
    #           +"\t"+str(meta['total_inserts'])
    #           +"\t"+str(meta['total_deletes'])
    #           +"\t"+str(meta['binary']))

do_things(owner, repo_name, numstat_object, repo_path)
