import dateutil.parser
import numpy as np
import pyarrow as pa

import w3hn.hadoop.parquet_util as pq_util
from w3hn.datapipe.ingest.ingester import Ingester
from w3hn.log.log_init import logger

class RepoFileIngester(Ingester):

    # ----------------------------------------------------
    # Constants
    # ----------------------------------------------------
    
    COLUMN_NAMES = [
        "owner", "repo_name", "owner_repo", "file_path",
        "num_commits", "first_commit_date", "last_commit_date",
        "total_inserts", "total_deletes", "binary",
        "partition_key"
    ]

    EXPLICIT_SCHEMA = pa.schema([
        pa.field("owner", pa.string()),
        pa.field("repo_name", pa.string()),
        pa.field("owner_repo", pa.string()),
        pa.field("file_path", pa.string()),
        pa.field("num_commits", pa.int64()),
        pa.field("first_commit_date", pa.timestamp('us', tz='UTC')),
        pa.field("last_commit_date", pa.timestamp('us', tz='UTC')),
        pa.field("total_inserts", pa.int64()),
        pa.field("total_deletes", pa.int64()),
        pa.field("binary", pa.int8()),
        Ingester.PARTITION_KEY_FIELD,
    ])
    
    # ----------------------------------------------------
    # Static API
    # ----------------------------------------------------

    # repo_tuple_array = [repo_tuple]
    # repo_tuple = (owner, repo_name, blame_object, deps_object, numstat_object)
    # example: [('apache', 'ant', json.loads(blame_json),
    #            json.loads(deps_json), json.loads(numstat_json))]
    def update_repos(repo_tuple_array):
        ingester = RepoFileIngester()
        Ingester.update_repos_using_ingester(ingester, repo_tuple_array)

    # ----------------------------------------------------
    # Instance Initialization
    # ----------------------------------------------------
    def __init__(self,
                 aws_profile='w3hn-admin',
                 bucket='deadmandao',
                 raw_path='web3hackernetwork/data_pipeline_v2/raw'):
        super().__init__(aws_profile, bucket, raw_path, 'repo_file')
        self.log = logger(__file__)

    # ----------------------------------------------------
    # Instance API
    # ----------------------------------------------------

    def extract_data(self, owner, repo_name,
                     blame_map=None, dependency_map=None, numstat=None):
        code_suffixes = ['.js', '.py', '.c', '.java', '.go', '.ts',
                         '.cpp', '.php', '.rb', '.cs', '.cc', '.rs',
                         '.tsx', '.scala', '.jsx']

        raw_dataset = dict()
        synthetic_key = pq_util.repo_partition_key(owner, repo_name)
        synthetic_key = f'pk_{synthetic_key}'
        for commit in numstat:
            commit_date = dateutil.parser.isoparse(commit['Date'])
            num_files = len(commit['file_list'])
            if num_files > 1000:
                self.log.error(f'{num_files} in one commit in {owner} {repo_name}')
                continue
            for file_path in commit['file_list']:
                if '.' not in file_path: continue
                extension_length = file_path[::-1].index('.') + 1
                start_of_the_ending = len(file_path) - extension_length
                extension = file_path[start_of_the_ending:]
                if extension not in code_suffixes: continue
                file_entry = commit['file_list'][file_path]
                if file_path in raw_dataset:
                    meta = raw_dataset[file_path]
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
                    raw_dataset[file_path] = meta
        return raw_dataset

    def create_table(self, repo_files, owner, repo_name):
        unique_files = list(repo_files.keys())
        unique_files.sort()
        count = len(unique_files)
        synthetic_key = pq_util.repo_partition_key(owner, repo_name)
        owners = [owner for i in range(count)]
        repo_names = [repo_name for i in range(count)]
        file_paths = np.array(unique_files)
        owner_repos = [f'{owner}\t{repo_name}' for i in range(count)]
        partition_keys = [synthetic_key for i in range(count)]
        
        num_commitss = list()
        first_commit_dates = list()
        last_commit_dates = list()
        total_insertss = list()
        total_deletess = list()
        binarys = list()
        for index in range(count):
            file_path = unique_files[index]
            meta = repo_files[file_path]
            num_commitss.append(meta['num_commits'])
            first_commit_dates.append(meta['first_commit_date'])
            last_commit_dates.append(meta['last_commit_date'])
            total_insertss.append(meta['total_inserts'])
            total_deletess.append(meta['total_deletes'])
            binarys.append(meta['binary'])

        data = [
            pa.array(owners), pa.array(repo_names), pa.array(owner_repos),
            pa.array(file_paths), pa.array(num_commitss),
            pa.array(first_commit_dates), pa.array(last_commit_dates),
            pa.array(total_insertss), pa.array(total_deletess),
            pa.array(binarys), pa.array(partition_keys)
        ]
        batch = pa.RecordBatch.from_arrays(data, RepoFileIngester.COLUMN_NAMES)
        inferred_table = pa.Table.from_batches([batch])
        explicit_table = inferred_table.cast(RepoFileIngester.EXPLICIT_SCHEMA)
        return explicit_table
