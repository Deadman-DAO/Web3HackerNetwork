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
from repo_file_parquet import RepoFileParquet

bucket = "numstat-bucket"
raw_path = "data_pipeline/raw"
repo_file_path = raw_path+"/repo_file"

owner = 'apache'
repo_name = 'ant'
# owner = 'cilium'
# repo_name = 'cilium'

print(datetime.datetime.now())
s3_util = S3Util(profile="enigmatt")
numstat_object = s3_util.get_numstat(owner, repo_name)
print(datetime.datetime.now())
repo_file_parquet = RepoFileParquet()
repo_file_parquet.update_repo(owner, repo_name, numstat_object)
print(datetime.datetime.now())

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
