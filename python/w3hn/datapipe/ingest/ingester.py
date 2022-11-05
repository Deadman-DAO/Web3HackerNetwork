from abc import ABC, abstractmethod

import datetime
import pyarrow as pa
import pyarrow.parquet as pq

import w3hn.hadoop.parquet_util as pq_util
from w3hn.aws.aws_util import S3Util

class Ingester(ABC):

    @abstractmethod
    def extract_data(self, owner, repo_name,
                     blame_map=None, dependency_map=None, numstat=None):
        pass
    @abstractmethod
    def create_table(self, new_data, owner, repo_name):
        pass

    # Same across entire raw tier. (or, if not, needs big rethink)
    PARTITION_KEY_FIELD = pa.field("partition_key", pa.string())

    def update_repos_using_ingester(ingester, repo_tuple_array):
        print(f'ingester update_repos_using_ingester [{len(repo_tuple_array)}]')
        synth_dict = dict()
        for repo_tuple in repo_tuple_array:
            # print(f'ingester entered repo_tuple loop')
            owner = repo_tuple[0]
            repo_name = repo_tuple[1]
            synthetic_key = pq_util.repo_partition_key(owner, repo_name)
            if synthetic_key not in synth_dict:
                synth_dict[synthetic_key] = list()
            synth_dict[synthetic_key].append(repo_tuple)
        for key in synth_dict:
            repo_tuple_list = synth_dict[key]
            num = len(repo_tuple_list)
            print(str(datetime.datetime.now()))
            print(f'ingester processing {num} numstats in synth key {key}')
            new_table_tuples = list()
            count = 0
            numtuples = len(repo_tuple_list)
            for repo_tuple in repo_tuple_list:
                owner = repo_tuple[0]
                repo_name = repo_tuple[1]
                numstat_object = repo_tuple[4]
                print(f'{type(ingester)} extracting data from {owner} {repo_name}')
                new_data = ingester.extract_data(owner,
                                                 repo_name,
                                                 blame_map=repo_tuple[2],
                                                 dependency_map=repo_tuple[3],
                                                 numstat=repo_tuple[4])
                new_table = ingester.create_table(new_data, owner, repo_name)
                new_table_tuple = (owner, repo_name, new_table)
                new_table_tuples.append(new_table_tuple)
                count += 1
                if count % 10 == 0:
                    print(f'ingester {count} of {numtuples} numstats done')
            print(str(datetime.datetime.now()))
            print(f'ingester merging old table with {numtuples} new tables')
            full_table = ingester.merge_batch(synthetic_key, new_table_tuples)
            ingester.write_parquet(owner, repo_name, full_table)

    # ----------------------------------------------------
    # Instance Initialization
    # ----------------------------------------------------
    def __init__(self, aws_profile, bucket, raw_path, path_suffix):
        self.s3_util = S3Util(profile=aws_profile, bucket_name=bucket)
        self.bucket = bucket
        self.raw_path = raw_path
        self.dataset_path = f'{self.raw_path}/{path_suffix}'
    
    # ----------------------------------------------------
    # Instance API
    # ----------------------------------------------------

    def instance_update_repos(self, repo_tuple_array):
        Ingester.update_repos_using_ingester(self, repo_tuple_array)

    # This is common across all ingesters. Check the 'self.' refs to
    # ensure they can be pulled up.
    def load_existing_for_batch(self, partition_key, owner_repos):
        partition_path = f'{self.dataset_path}/partition_key={partition_key}'
        if self.s3_util.path_exists(partition_path):
            print(f'repo/file found existing dataset {partition_path}')
            bucket_path = f'{self.bucket}/{partition_path}'
            s3fs = self.s3_util.pyarrow_fs()
            owner_repo_filter = ('owner_repo', 'not in', owner_repos)
            filters = [owner_repo_filter]
            legacy_dataset = pq.ParquetDataset(bucket_path,
                                               filesystem=s3fs,
                                               partitioning="hive",
                                               filters=filters)
            print(str(datetime.datetime.now()))
            print(f'{__file__}: about to read parquet')
            table = legacy_dataset.read()
            numrows = table.num_rows
            print(f'{__file__}: old table has {numrows} rows after filter')
            if numrows == 0: return None
            column = [partition_key for i in range(numrows)]
            key_field = Ingester.PARTITION_KEY_FIELD
            table = table.add_column(table.num_columns, key_field, [column])
            return table
        else:
            return None

    # this is common aross all ingesters, check 'self.load_existing_for_batch'
    def merge_batch(self, partition_key, new_table_tuples):
        # tuple shape = (owner, repo_name, new_table)
        owner_repos = list()
        tables = list()
        for new_table_tuple in new_table_tuples:
            owner_repo = f'{new_table_tuple[0]}\t{new_table_tuple[1]}'
            owner_repos.append(owner_repo)
            new_table = new_table_tuple[2]
            tables.append(new_table)
            # print(f'{__file__}: new table rows: {new_table.num_rows}')
        live_table = self.load_existing_for_batch(partition_key, owner_repos)
        if live_table != None:
            tables.append(live_table)
            print(f'{__file__}: old table rows: {live_table.num_rows}')
        merged_table = pa.concat_tables(tables, promote=False)
        print(f'{__file__}: merged table rows: {merged_table.num_rows}')
        return merged_table

    # this is common across ingesters which include "file_path" as the
    # first sort element after owner, repo_name (currently all)
    def write_parquet(self, owner, repo_name, table):
        # print(table.to_pandas())
        # return
        s3fs = self.s3_util.pyarrow_fs()
        bucket_path = f'{self.bucket}/{self.dataset_path}'
        partition_key = pq_util.repo_partition_key(owner, repo_name)
        partition_path = f'{self.dataset_path}/partition_key={partition_key}'
        print(f'{__file__}: sorting')
        print(str(datetime.datetime.now()))
        table.sort_by([('owner', 'ascending'),
                       ('repo_name', 'ascending'),
                       ('file_path', 'ascending')])
        print(f'{__file__}: writing {self.bucket}/{partition_path}')
        print(str(datetime.datetime.now()))
        if self.s3_util.path_exists(partition_path):
            print(f'{__file__}: deleting {self.bucket}/{partition_path}')
            s3fs.delete_dir(f'{self.bucket}/{partition_path}')
        else:
            print(f'{__file__}: no delete at {self.bucket}/{partition_path}')
        print(str(datetime.datetime.now()))
        pq.write_to_dataset(table,
                            root_path=bucket_path,
                            partition_cols=['partition_key'],
                            filesystem=s3fs)
        print(f'{__file__}: write complete')
        print(str(datetime.datetime.now()))
