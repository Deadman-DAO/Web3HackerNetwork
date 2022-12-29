from abc import ABC, abstractmethod

import pyarrow as pa
import pyarrow.parquet as pq

import w3hn.hadoop.parquet_util as pq_util
from w3hn.aws.aws_util import S3Util
import w3hn.log.log_init as log_init
from collections import namedtuple

class Ingester(ABC):

    @abstractmethod
    def extract_data(self, owner, repo_name, json_object):
        pass
    @abstractmethod
    def create_table(self, new_data, owner, repo_name):
        pass

    # Same across entire raw tier. (or, if not, needs big rethink)
    PARTITION_KEY_FIELD = pa.field("partition_key", pa.string())

    def update_repos_using_ingester(ingester, repo_tuple_array):
        log = log_init.logger(__file__)
        log.info(f'update_repos_using_ingester({type(ingester)}, [{len(repo_tuple_array)}])')
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
            log.info(f'ingester processing {num} numstats in synth key {key}')
            new_table_tuples = list()
            numtuples = len(repo_tuple_list)
            for repo_tuple in repo_tuple_list:
                owner = repo_tuple[0]
                repo_name = repo_tuple[1]
                log.debug(f'{type(ingester)} extracting data from {owner} {repo_name}')
                json_object = repo_tuple[2]
                new_data = ingester.extract_data(owner, repo_name, json_object)
                new_table = ingester.create_table(new_data, owner, repo_name)
                new_table_tuple = (owner, repo_name, new_table)
                new_table_tuples.append(new_table_tuple)
            log.info(f'ingester merging old table with {numtuples} new tables')
            full_table = ingester.merge_batch(synthetic_key, new_table_tuples)
            ingester.write_parquet(owner, repo_name, full_table)

    # ----------------------------------------------------
    # Instance Initialization
    # ----------------------------------------------------
    def __init__(self, aws_profile, bucket, raw_path, path_suffix, sort_by=[('owner', 'ascending'),
                                                                            ('repo_name', 'ascending'),
                                                                            ('file_path', 'ascending')]):
        self.log = log_init.logger(__file__)
        self.s3_util = S3Util(profile=aws_profile, bucket_name=bucket)
        self.bucket = bucket
        self.raw_path = raw_path
        self.dataset_path = f'{self.raw_path}/{path_suffix}'
        self.sort_by = sort_by
    
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
            self.log.info(f'repo/file found existing dataset {partition_path}')
            bucket_path = f'{self.bucket}/{partition_path}'
            s3fs = self.s3_util.pyarrow_fs()
            owner_repo_filter = ('owner_repo', 'not in', owner_repos)
            filters = [owner_repo_filter]
            legacy_dataset = pq.ParquetDataset(bucket_path,
                                               filesystem=s3fs,
                                               partitioning="hive",
                                               filters=filters)
            self.log.info(f'about to read parquet')
            table = legacy_dataset.read()
            numrows = table.num_rows
            self.log.info(f'old table retained {numrows} rows')
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
            owner_repo = f'{new_table_tuple[0]}/{new_table_tuple[1]}'
            owner_repos.append(owner_repo)
            new_table = new_table_tuple[2]
            tables.append(new_table)
            self.log.debug(f'new table rows: {new_table.num_rows}')
        live_table = self.load_existing_for_batch(partition_key, owner_repos)
        if live_table != None:
            tables.append(live_table)
            self.log.debug(f'old table rows: {live_table.num_rows}')
        merged_table = pa.concat_tables(tables, promote=False)
        self.log.debug(f'merged table rows: {merged_table.num_rows}')
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
        self.log.debug(f'sorting')
        table.sort_by(self.sort_by)
        self.log.info(f'writing {self.bucket}/{partition_path}')
        if self.s3_util.path_exists(partition_path):
            self.log.info(f'deleting {self.bucket}/{partition_path}')
            s3fs.delete_dir(f'{self.bucket}/{partition_path}')
        else:
            self.log.info(f'no delete at {self.bucket}/{partition_path}')
        pq.write_to_dataset(table,
                            root_path=bucket_path,
                            partition_cols=['partition_key'],
                            filesystem=s3fs)
        self.log.info(f'write complete')
