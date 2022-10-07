import bz2
import json
import datetime
import dateutil.parser
import hashlib
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

print(datetime.datetime.now())
owner = 'apache'
repo_name = 'ant'
repo_path = '../../data/bob/numstat/'+owner+'/'+repo_name
numstat_path = repo_path+'/log_numstat.out.json.bz2'
numstat_raw = ''
with open(numstat_path, 'rb') as r:
    numstat_raw = r.read()

numstat_str = bz2.decompress(numstat_raw)
numstat_object = json.loads(numstat_str)
print(datetime.datetime.now())

def synthetic_partition_key(owner, repo_name):
    partition_key = owner + "\t" + repo_name
    key_hash = hashlib.md5(partition_key.encode('utf-8')).hexdigest()
    synthetic_key = key_hash[slice(0, 2)]
    return synthetic_key

def do_things(owner, repo_name, numstat_object, repo_path):
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
    unique_files = list(repo_files.keys())
    unique_files.sort()
    
    count = len(unique_files)
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

    data = [col_partition_key, col_owner, col_repo_name, col_file_path,
            col_num_commits, col_first_commit_date, col_last_commit_date,
            col_total_inserts, col_total_deletes, col_binary]
    column_names = ["partition_key", "owner", "repo_name", "file_path",
                    "num_commits", "first_commit_date", "last_commit_date",
                    "total_inserts", "total_deletes", "binary"]
    batch = pa.RecordBatch.from_arrays(data, column_names)
    inferred_table = pa.Table.from_batches([batch])
    explicit_fields = [
        pa.field("partition_key", pa.string()),
        pa.field("owner", pa.string()),
        pa.field("repo_name", pa.string()),
        pa.field("file_path", pa.string()),
        pa.field("num_commits", pa.int64()),
        pa.field("first_commit_date", pa.timestamp('s', tz='+00:00')),
        pa.field("last_commit_date", pa.timestamp('s', tz='+00:00')),
        pa.field("total_inserts", pa.int64()),
        pa.field("total_deletes", pa.int64()),
        pa.field("binary", pa.int8())
    ]
    explicit_schema = pa.schema(explicit_fields)
    explicit_table = inferred_table.cast(explicit_schema)
    pq.write_to_dataset(explicit_table,
                        root_path='repo_file',
                        partition_cols=['partition_key'])
    

do_things(owner, repo_name, numstat_object, repo_path)
print(datetime.datetime.now())

table = pq.read_table("repo_file")
print(table.to_pandas())
