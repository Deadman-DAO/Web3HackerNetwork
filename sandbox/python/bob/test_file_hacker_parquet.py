import datetime
# import dateutil.parser
# import duckdb
# import numpy as np
# import pyarrow as pa
# import pyarrow.parquet as pq
import sys

sys.path.append("../../../python/lib")
from aws_util import S3Util
import parquet_util as pq_util
from file_hacker_parquet import FileHackerParquet

# bucket = "numstat-bucket"
# raw_path = "data_pipeline/raw"
# file_hacker_path = raw_path+"/file_hacker"

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
    with open('numstat-20kplus.log', 'r') as f:
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
        if partition_key < '13':
            print(f'skipping {partition_key}')
            continue
        else:
            print(f'{partition_key} is greater than 01')
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
            FileHackerParquet.update_repos(repo_tuple_array)
    # for numstat_tuple in numstat_tuples:
    #     try:
    #         now = datetime.datetime.now()
    #         delta = now - start
    #         per = delta / count
    #         expected = per * len(lines)
    #         print(f'{delta} {expected} loading numstat {count} of {len(lines)} for {owner} {repo_name}')
    #         numstat_object = numstat_s3_util.get_numstat(owner, repo_name)
    #         repo_tuple = (owner, repo_name, numstat_object)
    #         repo_tuple_array.append(repo_tuple)
    #     except Exception as error:
    #         print(f'error reading numstat {owner} {repo_name}: {error}')
    #         None # broken numstat, skip this repo
    # FileHackerParquet.update_repos(repo_tuple_array)
    
multi_phile()

# numstat_path_list = list()
# with open('numstat-sorted.log', 'r') as f:
#     for line in f.readlines():
#         line = line.strip()
#         tail = line[slice(line.index('\t') + 1, len(line))]
#         numstat_path_list.append(tail)
# update_slice = slice(len(numstat_path_list) - 20000, len(numstat_path_list))
# create_multiple_repo_files_parquet(numstat_path_list[update_slice])

# s3fs = s3_util.pyarrow_fs()
# legacy_dataset = pq.ParquetDataset(f'{bucket}/{repo_file_path}',
#                                    filesystem=s3fs,
#                                    partitioning="hive")
# legacy_table = legacy_dataset.read()#to_table()

# print()
# print("What Was Written:")
# print(legacy_table.to_pandas())
