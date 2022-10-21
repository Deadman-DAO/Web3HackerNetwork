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
sys.path.insert(0, f'{root_path}/python')
# ---------- Local Libraries -------------------
from w3hn.datapipe.ingest.file_hacker_commit import FileHackerCommitIngester
from w3hn.datapipe.ingest.repo_file import RepoFileIngester
from w3hn.aws.aws_util import S3Util
import w3hn.hadoop.parquet_util as pq_util
# ----------------------------------------------

sample_path = f'{root_path}/sandbox/python/bob/data/'
# nstat_log = f'{sample_path}/nstat-medium-sample.log'
# nstat_log = f'{sample_path}/nstat-medium-overlap-sample.log'
# nstat_log = f'{sample_path}/numstat-20kplus-reverse.log'
nstat_log = f'{sample_path}/nstat-5k-20k.log'

low_partition_limit = '00' # '00' for all
high_partition_limit = 'ff' # 'ff' for all

numstat_s3_util = S3Util(profile="enigmatt")

def single_phile():
    owner = 'apache'
    repo_name = 'ant'
    owner = 'cilium'
    repo_name = 'cilium'

    print(datetime.datetime.now())
    s3_util = S3Util(profile="enigmatt")
    numstat_object = s3_util.get_numstat(owner, repo_name)
    print(datetime.datetime.now())
    #repo_file_parquet = RepoFileParquet()
    FileHackerParquet.update_repo(owner, repo_name, numstat_object)
    print(datetime.datetime.now())

def multi_phile():
    # repo_tuple_array = list()
    count = 0
    start = datetime.datetime.now()
    numstat_tuple_dict = dict()
    with open(nstat_log, 'r') as f:
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
        # count = 0
        #     for numstat_tuple in numstat_tuple_list:
        #         count += 1
        #         owner = numstat_tuple[0]
        #         repo_name = numstat_tuple[1]
        #         result = load_numstat(repo_tuple_array, owner, repo_name)
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
            fh_thread.start()
            rf_thread.start()
            fh_thread.join()
            rf_thread.join()

def load_numstat(numstat_tuple):
    owner = numstat_tuple[0]
    repo_name = numstat_tuple[1]
    try:
        # print(f'reading numstat {count} of {len(numstat_tuple_list)}'
        #       f' for partition {partition_key} {owner} {repo_name}')
        print(f'reading numstat for partition {owner} {repo_name}')
        numstat_object = numstat_s3_util.get_numstat(owner, repo_name)
        repo_tuple = (owner, repo_name, numstat_object)
        return repo_tuple
    except Exception as error:
        print(f'error reading numstat {owner} {repo_name}: {error}')
    return None

def update_file_hacker(repo_tuple_array):
    #FileHackerCommitIngester.update_repos(repo_tuple_array)
    print(f'not running update_file_hacker on {len(repo_tuple_array)} repo_tuples')
    None

def update_repo_file(repo_tuple_array):
    #RepoFileIngester.update_repos(repo_tuple_array)
    print(f'not running update_repo_file on {len(repo_tuple_array)} repo_tuples')
    None
            
multi_phile()
