# ========= External Libraries =================
import datetime
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
# ----------------------------------------------

# ========== Project Root Path =================
this_path = os.path.abspath(sys.path[0])
project_dir = 'Web3HackerNetwork'
w3hndex = this_path.index(project_dir)
root_path = this_path[0:w3hndex + len(project_dir)]
# ---------- Local Library Path ----------------
# sys.path.insert(0, f'{root_path}/python')
# ---------- Local Libraries -------------------
from w3hn.datapipe.ingest.file_hacker_commit import FileHackerCommitIngester
from w3hn.datapipe.ingest.repo_file import RepoFileIngester
from w3hn.datapipe.ingest.dependency import DependencyIngester
from w3hn.aws.aws_util import S3Util
import w3hn.hadoop.parquet_util as pq_util
# ----------------------------------------------

TEST_MODE = False

sample_path = f'{root_path}/python/sandbox/bob/data'
deps_log = f'{sample_path}/deps-425.log'

low_partition_limit = '00' # '00' for all
high_partition_limit = 'ff' # 'ff' for all

json_s3_util = S3Util(profile="enigmatt")

def multi_phile():
    # repo_tuple_array = list()
    count = 0
    start = datetime.datetime.now()
    numstat_tuple_dict = dict()
    with open(deps_log, 'r') as f:
        lines = f.readlines()
        for line in lines:
            count += 1
            # if count > 100: break
            line = line.strip()
            path = line[slice(line.index('\t') + 1, len(line))]
            tail = path[slice(path.index('/') + 1, len(path))]
            owner = tail[slice(0,tail.index('/'))]
            tail = tail[slice(tail.index('/') + 1, len(tail))]
            repo_name = tail[slice(0,tail.index('/'))]
            partition_key = pq_util.repo_partition_key(owner, repo_name)
            if partition_key not in numstat_tuple_dict:
                numstat_tuple_dict[partition_key] = list()
            numstat_tuple_dict[partition_key].append((owner, repo_name))
    keys = list(numstat_tuple_dict.keys())
    keys.sort()
    for partition_key in keys:
        if partition_key < low_partition_limit:
            print(f'skipping {partition_key}')
            continue
        elif partition_key > high_partition_limit:
            print(f'skipping {partition_key}')
            continue
        else:
            print(f'{partition_key} is greater than threshold')
        print(datetime.datetime.now())
        numstat_tuple_list = numstat_tuple_dict[partition_key]
        repo_tuple_array = list()
        with ThreadPoolExecutor(max_workers=10) as executor:
            threadmap = executor.map(load_numstat, numstat_tuple_list)
        for result in threadmap:
            if result != None:
                repo_tuple_array.append(result)
        print(datetime.datetime.now())
        if len(repo_tuple_array) > 0:
            #x = threading.Thread(target=thread_function, args=(1,))
            fh_thread = threading.Thread(target=update_file_hacker,
                                         args=(repo_tuple_array,))
            rf_thread = threading.Thread(target=update_repo_file,
                                         args=(repo_tuple_array,))
            dep_thread = threading.Thread(target=update_dependency,
                                          args=(repo_tuple_array,))
            # fh_thread.start()
            # rf_thread.start()
            dep_thread.start()
            # fh_thread.join()
            # rf_thread.join()
            dep_thread.join()

def load_numstat(numstat_tuple):
    owner = numstat_tuple[0]
    repo_name = numstat_tuple[1]
    try:
        # print(f'reading numstat {count} of {len(numstat_tuple_list)}'
        #       f' for partition {partition_key} {owner} {repo_name}')
        print(f'reading numstat for partition {owner} {repo_name}')
        blame_object = None #json_s3_util.get_blame_map(owner, repo_name)
        deps_object = json_s3_util.get_dependency_map(owner, repo_name)
        numstat_object = None #json_s3_util.get_numstat(owner, repo_name)
        repo_tuple = (owner, repo_name, blame_object, deps_object, numstat_object)
        return repo_tuple
    except Exception as error:
        print(f'error reading numstat {owner} {repo_name}: {error}')
    return None

def update_file_hacker(repo_tuple_array):
    if TEST_MODE:
        print(f'not running update_file_hacker on {len(repo_tuple_array)} repo_tuples')
    else:
        FileHackerCommitIngester.update_repos(repo_tuple_array)

def update_dependency(repo_tuple_array):
    if TEST_MODE:
        print(f'not running update_file_hacker on {len(repo_tuple_array)} repo_tuples')
    else:
        DependencyIngester.update_repos(repo_tuple_array)

def update_repo_file(repo_tuple_array):
    if TEST_MODE:
        print(f'not running update_repo_file on {len(repo_tuple_array)} repo_tuples')
    else:
        RepoFileIngester.update_repos(repo_tuple_array)
            
multi_phile()
