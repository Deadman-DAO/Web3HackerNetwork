import datetime
import os
import sys
import threading

relative_lib = "../../../python"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), relative_lib))
from w3hn.datapipe.ingest.file_hacker_commit import FileHackerCommitIngester
from w3hn.datapipe.ingest.repo_file import RepoFileIngester
from w3hn.aws.aws_util import S3Util
import w3hn.hadoop.parquet_util as pq_util

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
    numstat_s3_util = S3Util(profile="enigmatt")
    start = datetime.datetime.now()
    numstat_tuple_dict = dict()
    # nstat_log = 'data/nstat-medium-sample.log'
    # nstat_log = 'data/nstat-medium-overlap-sample.log'
    nstat_log = 'data/numstat-20kplus-reverse.log'
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
        if partition_key < '00': #0b':
            print(f'skipping {partition_key}')
            continue
        else:
            print(f'{partition_key} is greater than threshold')
        print(datetime.datetime.now())
        numstat_tuple_list = numstat_tuple_dict[partition_key]
        repo_tuple_array = list()
        count = 0
        for numstat_tuple in numstat_tuple_list:
            count += 1
            owner = numstat_tuple[0]
            repo_name = numstat_tuple[1]
            try:
                print(f'reading numstat {count} of {len(numstat_tuple_list)}'
                      f' for partition {partition_key} {owner} {repo_name}')
                numstat_object = numstat_s3_util.get_numstat(owner, repo_name)
                repo_tuple = (owner, repo_name, numstat_object)
                repo_tuple_array.append(repo_tuple)
            except Exception as error:
                print(f'error reading numstat {owner} {repo_name}: {error}')
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

def update_file_hacker(repo_tuple_array):
    FileHackerCommitIngester.update_repos(repo_tuple_array)

def update_repo_file(repo_tuple_array):
    # RepoFileIngester.update_repos(repo_tuple_array)
    None
            
multi_phile()
