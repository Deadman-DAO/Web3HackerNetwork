import datetime
import dateutil.parser
import duckdb
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from aws_util import S3Util
import parquet_util as pq_util

class FileHackerParquet:
    # ----------------------------------------------------
    # Constants
    # ----------------------------------------------------
    PARTITION_KEY_FIELD = pa.field("partition_key", pa.string())
    EXPLICIT_SCHEMA = pa.schema([
            pa.field("owner", pa.string()),
            pa.field("repo_name", pa.string()),
            pa.field("owner_repo", pa.string()),
            pa.field("file_path", pa.string()),
            pa.field("author", pa.string()),
            pa.field("commit_date", pa.timestamp('us', tz='UTC')),
            # pa.field("num_commits", pa.int64()),
            # pa.field("first_commit_date", pa.timestamp('us', tz='UTC')),
            # pa.field("last_commit_date", pa.timestamp('us', tz='UTC')),
            pa.field("total_inserts", pa.int64()),
            pa.field("total_deletes", pa.int64()),
            pa.field("binary", pa.int8()),
            PARTITION_KEY_FIELD,
        ])
    
    # ----------------------------------------------------
    # Static API
    # ----------------------------------------------------
    def update_repo(owner, repo_name, numstat_object, repo_path="ignored"):
        pq_maker = FileHackerParquet()
        synthetic_key= pq_util.repo_partition_key(owner, repo_name)
        live_table = pq_maker.load_existing(synthetic_key)
        raw_dataset = pq_maker.extract_data(owner,
                                       repo_name,
                                       numstat_object)
        new_table = pq_maker.create_table(raw_dataset, owner, repo_name)
        merged_table = pq_maker.merge(owner, repo_name, live_table, new_table)
        pq_maker.write_parquet(owner, repo_name, merged_table)

    def update_repos(repo_tuple_array):
        synth_dict = dict()
        for repo_tuple in repo_tuple_array:
            owner = repo_tuple[0]
            repo_name = repo_tuple[1]
            synthetic_key = pq_util.repo_partition_key(owner, repo_name)
            if synthetic_key not in synth_dict:
                synth_dict[synthetic_key] = list()
            synth_dict[synthetic_key].append(repo_tuple)
        fhp = FileHackerParquet()
        for key in synth_dict:
            repo_tuple_list = synth_dict[key]
            num = len(repo_tuple_list)
            print()
            print(f'processing {num} repos in synth key {key}')
            # live_table = fhp.load_existing(key)
            # if live_table != None:
            #     print(f'finished reading the existing data')
            new_table_tuples = list()
            for repo_tuple in repo_tuple_list:
                owner = repo_tuple[0]
                repo_name = repo_tuple[1]
                numstat_object = repo_tuple[2]
                print(f'adding {owner} {repo_name} to key {key}')
                new_data = fhp.extract_data(owner, repo_name, numstat_object)
                new_table = fhp.create_table(new_data, owner, repo_name)
                # print(str(new_table.to_pandas()))
                new_table_tuple = (owner, repo_name, new_table)
                new_table_tuples.append(new_table_tuple)
            print(f'merging old table with {len(repo_tuple_list)} new tables')
            full_table = fhp.merge_batch(synthetic_key, new_table_tuples)
            # def merge_batch(self, partition_key, new_table_tuples):
            #     #(owner, repo_name, new_table)
            #     live_table = fhp.merge(owner, repo_name, live_table, new_table)
            #     # print(str(live_table.to_pandas()))
            fhp.write_parquet(owner, repo_name, full_table)

    # ----------------------------------------------------
    # Instance Initialization
    # ----------------------------------------------------
    def __init__(self,
                 aws_profile='w3hn-admin',
                 bucket='deadmandao',
                 raw_path='web3hackernetwork/data_pipeline/raw'):
        self.s3_util = S3Util(profile=aws_profile, bucket_name=bucket)
        self.bucket = bucket
        self.raw_path = raw_path
        self.dataset_path = self.raw_path+'/file_hacker'

    # ----------------------------------------------------
    # Instance API
    # ----------------------------------------------------
    def extract_data(self, owner, repo_name, numstat_object):
        raw_dataset = dict()
        synthetic_key = pq_util.repo_partition_key(owner, repo_name)
        for commit in numstat_object:
            # print(str(commit))
            commit_date_str = commit['Date']
            # commit_date = dateutil.parser.isoparse(commit_date_str)
            author = commit['Author']
            for file_path in commit['file_list']:
                file_entry = commit['file_list'][file_path]
                dict_key = (file_path, author, commit_date_str)
                if dict_key in raw_dataset:
                    meta = raw_dataset[dict_key]
                    # meta['num_commits'] += 1
                    # if commit_date < meta['first_commit_date']:
                    #     meta['first_commit_date'] = commit_date
                    # if commit_date > meta['last_commit_date']:
                    #         meta['last_commit_date'] = commit_date
                    meta['total_inserts'] += file_entry['inserts']
                    meta['total_deletes'] += file_entry['deletes']
                else:
                    meta = dict()
                    # meta['num_commits'] = 1
                    # meta['first_commit_date'] = commit_date
                    # meta['last_commit_date'] = commit_date
                    meta['total_inserts'] = file_entry['inserts']
                    meta['total_deletes'] = file_entry['deletes']
                    meta['binary'] = file_entry['binary']
                    raw_dataset[dict_key] = meta
        return raw_dataset

    def create_table(self, raw_dataset, owner, repo_name):
        unique_keys = list(raw_dataset.keys())
        unique_keys.sort()
        count = len(unique_keys)
        synthetic_key = pq_util.repo_partition_key(owner, repo_name)
        owner_array = [owner for i in range(count)]
        repo_name_array = [repo_name for i in range(count)]
        owner_repo_array = [f'{owner}\t{repo_name}' for i in range(count)]
        file_path_array = ['' for i in range(count)]
        author_array = ['' for i in range(count)]
        commit_date_array = [datetime.datetime.now() for i in range(count)]
        # num_commits_array = [0 for i in range(count)]
        # first_commit_date_array = [datetime.datetime.now() for i in range(count)]
        # last_commit_date_array = [datetime.datetime.now() for i in range(count)]
        total_inserts_array = [0 for i in range(count)]
        total_deletes_array = [0 for i in range(count)]
        binary_array = [0 for i in range(count)]
        partition_key_array = [f'{synthetic_key}' for i in range(count)]

        for index in range(count):
            dict_key = unique_keys[index]
            meta = raw_dataset[dict_key]
            file_path_array[index] = dict_key[0]
            author_array[index] = dict_key[1]
            commit_date_array[index] = dateutil.parser.isoparse(dict_key[2])
            # num_commits_array[index] = meta['num_commits']
            # first_commit_date_array[index] = meta['first_commit_date']
            # last_commit_date_array[index] = meta['last_commit_date']
            total_inserts_array[index] = meta['total_inserts']
            total_deletes_array[index] = meta['total_deletes']
            binary_array[index] = meta['binary']

        col_owner = pa.array(owner_array)
        col_repo_name = pa.array(repo_name_array)
        col_owner_repo = pa.array(owner_repo_array)
        col_file_path = pa.array(file_path_array)
        col_author = pa.array(author_array)
        col_commit_date = pa.array(commit_date_array)
        # col_num_commits = pa.array(num_commits_array)
        # col_first_commit_date = pa.array(first_commit_date_array)
        # col_last_commit_date = pa.array(last_commit_date_array)
        col_total_inserts = pa.array(total_inserts_array)
        col_total_deletes = pa.array(total_deletes_array)
        col_binary = pa.array(binary_array)
        col_partition_key = pa.array(partition_key_array)

        data = [col_owner, col_repo_name, col_owner_repo, col_file_path, col_author,
                col_commit_date,
                # col_num_commits, col_first_commit_date, col_last_commit_date,
                col_total_inserts, col_total_deletes, col_binary,
                col_partition_key]
        column_names = ["owner", "repo_name", "owner_repo", "file_path", "author",
                        "commit_date",
                        # "num_commits", "first_commit_date", "last_commit_date",
                        "total_inserts", "total_deletes", "binary",
                        "partition_key"]
        batch = pa.RecordBatch.from_arrays(data, column_names)
        inferred_table = pa.Table.from_batches([batch])
        explicit_table = inferred_table.cast(FileHackerParquet.EXPLICIT_SCHEMA)
        return explicit_table

    def load_existing(self, partition_key):
        partition_path = f'{self.dataset_path}/partition_key={partition_key}'
        if self.s3_util.path_exists(partition_path):
            print(f'Found existing dataset at {partition_path}')
            bucket_path = f'{self.bucket}/{self.dataset_path}'
            fs = self.s3_util.pyarrow_fs()
            partition_filter = [('partition_key', '=', partition_key)]
            legacy_dataset = pq.ParquetDataset(bucket_path,
                                               filesystem=fs,
                                               partitioning="hive",
                                               filters=partition_filter)
            print(f'about to read parquet')
            return legacy_dataset.read()
        else:
            return None

    def load_existing_for_batch(self, partition_key, owner_repos):
        partition_path = f'{self.dataset_path}/partition_key={partition_key}'
        if self.s3_util.path_exists(partition_path):
            print(f'Found existing dataset at {partition_path}')
            bucket_path = f'{self.bucket}/{partition_path}'
            s3fs = self.s3_util.pyarrow_fs()
            # partition_filter = ('partition_key', '=', partition_key)
            owner_repo_filter = ('owner_repo', 'not in', owner_repos)
            filters = [owner_repo_filter]# partition_filter, 
            legacy_dataset = pq.ParquetDataset(bucket_path,
                                               filesystem=s3fs,
                                               partitioning="hive",
                                               filters=filters)
            print(str(datetime.datetime.now()))
            print(f'about to read parquet')
            table = legacy_dataset.read()
            numrows = table.num_rows
            print(f'existing table contains {numrows} rows after filtering')
            if numrows == 0: return None
            column = [partition_key for i in range(numrows)]
            # print(str(column))
            # print(f'{len(column)}')
            # print(f'number of elements in column: {len(column)}')
            key_field = FileHackerParquet.PARTITION_KEY_FIELD
            table = table.add_column(table.num_columns, key_field, [column])
            return table
        else:
            return None
    
    def merge_batch(self, partition_key, new_table_tuples):
        #(owner, repo_name, new_table)
        owner_repos = list()
        tables = list()
        for new_table_tuple in new_table_tuples:
            owner_repo = f'{new_table_tuple[0]}\t{new_table_tuple[1]}'
            owner_repos.append(owner_repo)
            tables.append(new_table_tuple[2])
        # print('new table sample')
        # print(str(tables[0].schema))
        live_table = self.load_existing_for_batch(partition_key, owner_repos)
        if live_table != None:
            print(str(live_table.to_pandas()))
            print(str(live_table.schema))
            if live_table != None and live_table.num_rows > 0:
                tables.append(live_table)
        merged_table = pa.concat_tables(tables, promote=False)
        # merged_table = merged_table.sort_by([('owner','ascending'),
        #                                      ('repo_name','ascending'),
        #                                      ('file_path','ascending'),
        #                                      ('author','ascending'),
        #                                      ('commit_date','ascending')])
        return merged_table

    def merge(self, owner, repo_name, live_table, new_table):
        if live_table == None:
            return new_table
        else:
            partition_key = pq_util.repo_partition_key(owner, repo_name)
            owner_repo = f'{owner}\t{repo_name}'
            sql = f"""SELECT *
                       FROM live_table
                       WHERE partition_key = '{partition_key}'
                         AND owner_repo != '{owner_repo}'"""
            # (
            #                owner != '{owner}'
            #                OR
            #                repo_name != '{repo_name}'
            #              )"""
            duck_conn = duckdb.connect()
            other_table = duck_conn.execute(sql).arrow()
            merged_table = pa.concat_tables([other_table, new_table],
                                            promote=False)
            # merged_table = merged_table.sort_by([('owner','ascending'),
            #                                      ('repo_name','ascending'),
            #                                      ('file_path','ascending')])
            return merged_table

    def write_parquet(self, owner, repo_name, table):
        s3fs = self.s3_util.pyarrow_fs()
        bucket_path = f'{self.bucket}/{self.dataset_path}'
        partition_key = pq_util.repo_partition_key(owner, repo_name)
        partition_path = f'{self.dataset_path}/partition_key={partition_key}'
        if self.s3_util.path_exists(partition_path):
            print(f'deleting {self.bucket}/{partition_path}')
            s3fs.delete_dir(f'{self.bucket}/{partition_path}')
        else:
            print(f'no path to delete at {self.bucket}/{partition_path}')
        print(f'writing {self.bucket}/{partition_path}')
        # print(str(table.to_pandas()))
        # print(str(table.schema))
        table.sort_by([('owner', 'ascending'),
                       ('repo_name', 'ascending'),
                       ('file_path', 'ascending'),
                       ('author', 'ascending'),
                       ('commit_date','ascending')])
        pq.write_to_dataset(table,
                            root_path=bucket_path,
                            partition_cols=['partition_key'],
                            filesystem=s3fs)
        print('write complete')

