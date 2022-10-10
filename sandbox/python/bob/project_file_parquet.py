import configparser
import datetime
import dateutil.parser
import duckdb
import hashlib
import numpy as np
import os
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.fs as pafs
import sys

sys.path.append("../../../python/lib")
from aws_util import S3Util

# home_dir = os.path.expanduser("~")
# aws_credentials_path = home_dir+"/.aws/credentials"
raw_path = "numstat-bucket/data_pipeline/raw"
repo_file_path = raw_path+"/repo_file"

print(datetime.datetime.now())
owner = 'apache'
repo_name = 'ant'
#repo_name = 'kafka'
owner = 'cilium'
repo_name = 'cilium'

s3_util = S3Util(profile="enigmatt")
numstat_object = s3_util.get_numstat(owner, repo_name)

print(datetime.datetime.now())

def synthetic_partition_key(owner, repo_name):
    partition_key = owner + "\t" + repo_name
    key_hash = hashlib.md5(partition_key.encode('utf-8')).hexdigest()
    synthetic_key = key_hash[slice(0, 2)]
    return synthetic_key

def extract_repo_file_data(owner, repo_name, numstat_object):
    repo_files = dict()
    synthetic_key = synthetic_partition_key(owner, repo_name)
    for commit in numstat_object:
        #print(commit)
        commit_date = dateutil.parser.isoparse(commit['Date'])
        for file_path in commit['file_list']:
            file_entry = commit['file_list'][file_path]
            if file_path in repo_files:
                file_metadata = repo_files[file_path]
                file_metadata['num_commits'] += 1
                if commit_date < file_metadata['first_commit_date']:
                    file_metadata['first_commit_date'] = commit_date
                if commit_date > file_metadata['last_commit_date']:
                    file_metadata['last_commit_date'] = commit_date
                file_metadata['total_inserts'] += file_entry['inserts']
                file_metadata['total_deletes'] += file_entry['deletes']
            else:
                file_metadata = dict()
                file_metadata['num_commits'] = 1
                file_metadata['first_commit_date'] = commit_date
                file_metadata['last_commit_date'] = commit_date
                file_metadata['total_inserts'] = file_entry['inserts']
                file_metadata['total_deletes'] = file_entry['deletes']
                file_metadata['binary'] = file_entry['binary']
                repo_files[file_path] = file_metadata
    return repo_files

def create_table(repo_files):
    unique_files = list(repo_files.keys())
    unique_files.sort()
    count = len(unique_files)
    synthetic_key = synthetic_partition_key(owner, repo_name)
    partition_key_array = [synthetic_key for i in range(count)]
    owner_array = [owner for i in range(count)]
    repo_name_array = [repo_name for i in range(count)]
    file_path_array = np.array(unique_files)
    num_commits_array = [0 for i in range(count)]
    first_commit_date_array = [datetime.datetime.now() for i in range(count)]
    last_commit_date_array = [datetime.datetime.now() for i in range(count)]
    total_inserts_array = [0 for i in range(count)]
    total_deletes_array = [0 for i in range(count)]
    binary_array = [0 for i in range(count)]

    for index in range(count):
        file_path = unique_files[index]
        meta = repo_files[file_path]
        file_path_array[index] = file_path
        num_commits_array[index] = meta['num_commits']
        first_commit_date_array[index] = meta['first_commit_date']
        last_commit_date_array[index] = meta['last_commit_date']
        total_inserts_array[index] = meta['total_inserts']
        total_deletes_array[index] = meta['total_deletes']
        binary_array[index] = meta['binary']
    
    col_partition_key = pa.array(partition_key_array)
    col_owner = pa.array(owner_array)
    col_repo_name = pa.array(repo_name_array)
    col_file_path = pa.array(file_path_array)
    col_num_commits = pa.array(num_commits_array)
    col_first_commit_date = pa.array(first_commit_date_array)
    col_last_commit_date = pa.array(last_commit_date_array)
    col_total_inserts = pa.array(total_inserts_array)
    col_total_deletes = pa.array(total_deletes_array)
    col_binary = pa.array(binary_array)

    data = [col_owner, col_repo_name, col_file_path,
            col_num_commits, col_first_commit_date, col_last_commit_date,
            col_total_inserts, col_total_deletes, col_binary,
            col_partition_key]
    column_names = ["owner", "repo_name", "file_path",
                    "num_commits", "first_commit_date", "last_commit_date",
                    "total_inserts", "total_deletes", "binary",
                    "partition_key"]
    batch = pa.RecordBatch.from_arrays(data, column_names)
    inferred_table = pa.Table.from_batches([batch])
    explicit_fields = [
        pa.field("owner", pa.string()),
        pa.field("repo_name", pa.string()),
        pa.field("file_path", pa.string()),
        pa.field("num_commits", pa.int64()),
        pa.field("first_commit_date", pa.timestamp('us', tz='UTC')),#+00:00')),
        pa.field("last_commit_date", pa.timestamp('us', tz='UTC')),#+00:00')),
        pa.field("total_inserts", pa.int64()),
        pa.field("total_deletes", pa.int64()),
        pa.field("binary", pa.int8()),
        pa.field("partition_key", pa.string()),
    ]
    explicit_schema = pa.schema(explicit_fields)
    explicit_table = inferred_table.cast(explicit_schema)
    return explicit_table

# def get_s3fs():
#     credentials = configparser.ConfigParser()
#     credentials.read(filenames=[aws_credentials_path])
#     enigmatt_access_key = credentials.get("enigmatt", "aws_access_key_id")
#     enigmatt_secret_key = credentials.get("enigmatt", "aws_secret_access_key")
#     s3fs = pafs.S3FileSystem(access_key=enigmatt_access_key,
#                              secret_key=enigmatt_secret_key)
#     return s3fs

def read_partition_dataset(owner, repo_name, s3fs):
    partition_key = synthetic_partition_key(owner, repo_name)
    partition_path = repo_file_path
    dataset = pq.ParquetDataset(partition_path,
                                filesystem=s3fs,
                                partitioning="hive")
    return dataset

def update_parquet(owner, repo_name, table):
    s3fs = s3_util.pyarrow_fs()
    duck_conn = duckdb.connect()
    partition_key = synthetic_partition_key(owner, repo_name)
    partition_path = repo_file_path
    # s3fs = fs.FileSystem.from_uri("s3://")[0]
    # load existing dataset
    legacy_dataset = read_partition_dataset(owner, repo_name, s3fs)
    legacy_table = legacy_dataset.read()#to_table()
    #print(str(legacy_table.to_pandas()))
    
    # select from existing where (owner != owner or repo_name != repo_name)
    sql = f"""SELECT *
                FROM legacy_table
                WHERE partition_key = '{partition_key}'
                  AND (
                    owner != '{owner}'
                    OR
                    repo_name != '{repo_name}'
                  )"""
    other_repos_table = duck_conn.execute(sql).arrow()
    print("other repos dataset:")
    print(str(other_repos_table.to_pandas()))
    print("this repo dataset:")
    print(str(table.to_pandas()))
    # die die die my darling
    # append to table
    merged_table = pa.concat_tables([other_repos_table, table], promote=False)
    merged_table = merged_table.sort_by([('owner','ascending'),
                                         ('repo_name','ascending'),
                                         ('file_path','ascending')])
    # delete existing partition from S3
    s3fs.delete_dir(partition_path)
    # write merged partition dataset to S3
    pq.write_to_dataset(merged_table,
                        root_path='numstat-bucket/data_pipeline/raw/repo_file',
                        partition_cols=['partition_key'],
                        filesystem=s3fs)

def update_repo_files_parquet(owner, repo_name, numstat_object, repo_path="ignored"):
    repo_files = extract_repo_file_data(owner, repo_name, numstat_object)
    table = create_table(repo_files)
    #print(str(table.to_pandas()))
    update_parquet(owner, repo_name, table)


update_repo_files_parquet(owner, repo_name, numstat_object)
print(datetime.datetime.now())

s3fs = get_s3fs()
duck_conn = duckdb.connect()
legacy_dataset = read_partition_dataset(owner, repo_name, s3fs)
legacy_table = legacy_dataset.read()#to_table()

print()
print("What Was Written:")
print(legacy_table.to_pandas())

# to delete the file, I had to use the full path:
# $ aws s3 rm s3://numstat-bucket/data_pipeline/raw/repo_file/partition_key=e3/10330317b031417c8ef039acff04b420-0.parquet
# when I just used the partition_key=e3 dir, it did not delete
# ... duh - recursive :D
# $ aws s3 rm --recursive s3://numstat-bucket/data_pipeline/raw/repo_file/partition_key=e3/
