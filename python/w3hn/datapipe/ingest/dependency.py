import datetime
# import dateutil.parser
# import duckdb
# import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from w3hn.aws.aws_util import S3Util
import w3hn.hadoop.parquet_util as pq_util
from w3hn.datapipe.ingest.ingester import Ingester

class DependencyIngester(Ingester):

    # ----------------------------------------------------
    # Constants
    # ----------------------------------------------------
    

    # Unique for each ingester.
    COLUMN_NAMES = [
        "owner", "repo_name", "owner_repo", "file_path",
        "dependency", "partition_key"
    ]

    # Unique for each ingester.
    EXPLICIT_SCHEMA = pa.schema([
        pa.field("owner", pa.string()),
        pa.field("repo_name", pa.string()),
        pa.field("owner_repo", pa.string()),
        pa.field("file_path", pa.string()),
        pa.field("dependency", pa.string()),
        Ingester.PARTITION_KEY_FIELD,
    ])
    
    # ----------------------------------------------------
    # Static API
    # ----------------------------------------------------

    # repo_tuple_array = [repo_tuple]
    # repo_tuple = (owner, repo_name, blame_object, deps_object, numstat_object)
    # example: [('apache', 'ant', json.loads(blame_json),
    #            json.loads(deps_json), json.loads(numstat_json))]
    # 
    # if you're running a large number of repos across multiple
    # partition keys, you may want to collect by partition key
    # and only load one partition key worth of dependency.jsons
    # at a time, to keep memory down.
    #
    # Other than the debug printlines, I think this method is
    # generic for all Parquet updaters (file_hacker, repo_file,
    # and dependency, at time of writing)
    def update_repos(repo_tuple_array):
        synth_dict = dict()
        for repo_tuple in repo_tuple_array:
            owner = repo_tuple[0]
            repo_name = repo_tuple[1]
            synthetic_key = pq_util.repo_partition_key(owner, repo_name)
            if synthetic_key not in synth_dict:
                synth_dict[synthetic_key] = list()
            synth_dict[synthetic_key].append(repo_tuple)
        pq_tool = DependencyIngester()
        for key in synth_dict:
            repo_tuple_list = synth_dict[key]
            num = len(repo_tuple_list)
            print(str(datetime.datetime.now()))
            print(f'{__file__}: processing {num} jsons in synth key {key}')
            new_table_tuples = list()
            count = 0
            numtuples = len(repo_tuple_list)
            for repo_tuple in repo_tuple_list:
                owner = repo_tuple[0]
                repo_name = repo_tuple[1]
                json_object = repo_tuple[3]
                new_data = pq_tool.extract_data(owner, repo_name, json_object)
                new_table = pq_tool.create_table(new_data, owner, repo_name)
                new_table_tuple = (owner, repo_name, new_table)
                new_table_tuples.append(new_table_tuple)
                count += 1
                if count % 10 == 0:
                    print(f'{__file__}: {count} of {numtuples} done')
            print(str(datetime.datetime.now()))
            print(f'{__file__}: merging old with {numtuples} new tables')
            full_table = pq_tool.merge_batch(synthetic_key, new_table_tuples)
            pq_tool.write_parquet(owner, repo_name, full_table)
    
    # ----------------------------------------------------
    # Instance Initialization
    # ----------------------------------------------------

    # Only the suffix on self.dataset_path changes from one
    # parquet ingester to another.
    def __init__(self,
                 aws_profile='w3hn-admin',
                 bucket='deadmandao',
                 raw_path='web3hackernetwork/data_pipeline/raw'):
        self.s3_util = S3Util(profile=aws_profile, bucket_name=bucket)
        self.bucket = bucket
        self.raw_path = raw_path
        self.dataset_path = self.raw_path+'/dependency'

    # ----------------------------------------------------
    # Instance API
    # ----------------------------------------------------

    # Unique for each ingester.
    def extract_data(self, owner, repo_name, json_object):
        deps_set = set()
        for file_path, libs in json_object.items():
            for lib in libs:
                unique_key = f'{file_path}\t{lib}'
                deps_set.add(unique_key)
        sore_ted = list(deps_set)
        sore_ted.sort()
        return sore_ted

    # About 50% of this function is shared across all
    # parquet ingesters.
    def create_table(self, dep_pairs, owner, repo_name):
        count = len(dep_pairs)
        synthetic_key = pq_util.repo_partition_key(owner, repo_name)
        owners = [owner for i in range(count)]
        repo_names = [repo_name for i in range(count)]
        owner_repos = [f'{owner}\t{repo_name}' for i in range(count)]
        paths = list()
        libs = list()
        partition_keys = [synthetic_key for i in range(count)]

        for pair in dep_pairs:
            (path, lib) = pair.split('\t', 2)
            paths.append(path)
            libs.append(lib)

        data = [
            pa.array(owners), pa.array(repo_names), pa.array(owner_repos),
            pa.array(paths), pa.array(libs), pa.array(partition_keys)
        ]
        batch = pa.RecordBatch.from_arrays(data, DependencyIngester.COLUMN_NAMES)
        inferred_table = pa.Table.from_batches([batch])
        explicit_table = inferred_table.cast(DependencyIngester.EXPLICIT_SCHEMA)
        return explicit_table

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
            print(f'{__file__}: new table rows: {new_table.num_rows}')
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
        if self.s3_util.path_exists(partition_path):
            print(f'{__file__}: deleting {self.bucket}/{partition_path}')
            s3fs.delete_dir(f'{self.bucket}/{partition_path}')
        else:
            print(f'{__file__}: no delete at {self.bucket}/{partition_path}')
        print(f'{__file__}: sorting')
        print(str(datetime.datetime.now()))
        table.sort_by([('owner', 'ascending'),
                       ('repo_name', 'ascending'),
                       ('file_path', 'ascending')])
        print(f'{__file__}: writing {self.bucket}/{partition_path}')
        print(str(datetime.datetime.now()))
        pq.write_to_dataset(table,
                            root_path=bucket_path,
                            partition_cols=['partition_key'],
                            filesystem=s3fs)
        print(f'{__file__}: write complete')
        print(str(datetime.datetime.now()))
