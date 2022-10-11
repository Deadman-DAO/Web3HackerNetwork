import datetime
import dateutil.parser
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from aws_util import S3Util
import parquet_util as pq_util

class RepoFileParquet:
    def __init__(self,
                 aws_profile='w3hn-admin',
                 bucket='deadmandao',
                 raw_path='data_pipeline/raw'):
        self.s3_util = S3Util(profile=aws_profile, bucket_name=bucket)
        self.bucket = bucket
        self.raw_path = raw_path
        self.repo_file_path = self.raw_path+'/repo_file'

    def extract_repo_file_data(self, owner, repo_name, numstat_object):
        repo_files = dict()
        synthetic_key = pq_util.repo_partition_key(owner, repo_name)
        for commit in numstat_object:
            commit_date = dateutil.parser.isoparse(commit['Date'])
            for file_path in commit['file_list']:
                file_entry = commit['file_list'][file_path]
                if file_path in repo_files:
                    meta = repo_files[file_path]
                    meta['num_commits'] += 1
                    if commit_date < meta['first_commit_date']:
                        meta['first_commit_date'] = commit_date
                    if commit_date > meta['last_commit_date']:
                            meta['last_commit_date'] = commit_date
                    meta['total_inserts'] += file_entry['inserts']
                    meta['total_deletes'] += file_entry['deletes']
                else:
                    meta = dict()
                    meta['num_commits'] = 1
                    meta['first_commit_date'] = commit_date
                    meta['last_commit_date'] = commit_date
                    meta['total_inserts'] = file_entry['inserts']
                    meta['total_deletes'] = file_entry['deletes']
                    meta['binary'] = file_entry['binary']
                    repo_files[file_path] = meta
        return repo_files

    def create_table(self, repo_files, owner, repo_name):
        unique_files = list(repo_files.keys())
        unique_files.sort()
        count = len(unique_files)
        synthetic_key = pq_util.repo_partition_key(owner, repo_name)
        owner_array = [owner for i in range(count)]
        repo_name_array = [repo_name for i in range(count)]
        file_path_array = np.array(unique_files)
        num_commits_array = [0 for i in range(count)]
        first_commit_date_array = [datetime.datetime.now() for i in range(count)]
        last_commit_date_array = [datetime.datetime.now() for i in range(count)]
        total_inserts_array = [0 for i in range(count)]
        total_deletes_array = [0 for i in range(count)]
        binary_array = [0 for i in range(count)]
        partition_key_array = [synthetic_key for i in range(count)]

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

        col_owner = pa.array(owner_array)
        col_repo_name = pa.array(repo_name_array)
        col_file_path = pa.array(file_path_array)
        col_num_commits = pa.array(num_commits_array)
        col_first_commit_date = pa.array(first_commit_date_array)
        col_last_commit_date = pa.array(last_commit_date_array)
        col_total_inserts = pa.array(total_inserts_array)
        col_total_deletes = pa.array(total_deletes_array)
        col_binary = pa.array(binary_array)
        col_partition_key = pa.array(partition_key_array)

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
            pa.field("first_commit_date", pa.timestamp('us', tz='UTC')),
            pa.field("last_commit_date", pa.timestamp('us', tz='UTC')),
            pa.field("total_inserts", pa.int64()),
            pa.field("total_deletes", pa.int64()),
            pa.field("binary", pa.int8()),
            pa.field("partition_key", pa.string()),
        ]
        explicit_schema = pa.schema(explicit_fields)
        explicit_table = inferred_table.cast(explicit_schema)
        return explicit_table

    def merge_existing(owner, repo_name, table):
        partition_key = pq_util.repo_partition_key(owner, repo_name)
        legacy_dataset = pq.ParquetDataset(bucket + "/" + repo_file_path,
                                           filesystem=s3_util.pyarrow_fs(),
                                           partitioning="hive")
        legacy_table = legacy_dataset.read()
        sql = f"""SELECT *
                   FROM legacy_table
                   WHERE partition_key = '{partition_key}'
                     AND (
                       owner != '{owner}'
                       OR
                       repo_name != '{repo_name}'
                     )"""
        duck_conn = duckdb.connect()
        other_repos_table = duck_conn.execute(sql).arrow()
        merged_table = pa.concat_tables([other_repos_table, table],
                                        promote=False)
        merged_table = merged_table.sort_by([('owner','ascending'),
                                             ('repo_name','ascending'),
                                             ('file_path','ascending')])
        return merged_table

    def update_parquet(self, owner, repo_name, table):
        s3fs = self.s3_util.pyarrow_fs()
        partition_key = pq_util.repo_partition_key(owner, repo_name)
        partition_path = self.repo_file_path+f"/partition_key={partition_key}"
        if self.s3_util.path_exists(partition_path):
            print(f'Found existing dataset at {partition_path}')
            table = merge_existing(owner, repo_name, table)
            s3fs.delete_dir(f'{self.bucket}/{partition_path}')
        repo_file_bucket_path = f'{self.bucket}/{self.repo_file_path}'
        pq.write_to_dataset(table,
                            root_path=repo_file_bucket_path,
                            partition_cols=['partition_key'],
                            filesystem=s3fs)

    def update_repo(self, owner, repo_name,
                    numstat_object, repo_path="ignored"):
        repo_files = self.extract_repo_file_data(owner,
                                                 repo_name,
                                                 numstat_object)
        table = self.create_table(repo_files, owner, repo_name)
        self.update_parquet(owner, repo_name, table)
