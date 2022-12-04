import dateutil.parser
import json
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

import w3hn.hadoop.parquet_util as pq_util
from w3hn.datapipe.ingest.ingester import Ingester
from w3hn.log.log_init import logger
from w3hn.aws.aws_util import S3Util

log = logger(__file__)

class RecentRepoIngester():

    # ----------------------------------------------------
    # Constants
    # ----------------------------------------------------
    
    EXPLICIT_SCHEMA = pa.schema([
        pa.field("owner", pa.string()),
        pa.field("repo_name", pa.string()),
        pa.field("extension", pa.string()),
        pa.field("last_update", pa.timestamp('us', tz='UTC')),
        pa.field("license", pa.string()),
        pa.field("num_stars", pa.int32()),
        pa.field("num_forks", pa.int32()),
        Ingester.PARTITION_KEY_FIELD,
        # pa.field("owner", pa.string()),
        # pa.field("repo_name", pa.string()),
        # pa.field("owner_repo", pa.string()),
        # pa.field("file_path", pa.string()),
        # pa.field("num_commits", pa.int64()),
        # pa.field("first_commit_date", pa.timestamp('us', tz='UTC')),
        # pa.field("last_commit_date", pa.timestamp('us', tz='UTC')),
        # pa.field("total_inserts", pa.int64()),
        # pa.field("total_deletes", pa.int64()),
        # pa.field("binary", pa.int8()),
        # Ingester.PARTITION_KEY_FIELD,
    ])
    
    COLUMN_NAMES = EXPLICIT_SCHEMA.names

    # # ----------------------------------------------------
    # # Static API
    # # ----------------------------------------------------

    # # repo_tuple_array = [repo_tuple]
    # # repo_tuple = (owner, repo_name, blame_object, deps_object, numstat_object)
    # # example: [('apache', 'ant', json.loads(blame_json),
    # #            json.loads(deps_json), json.loads(numstat_json))]
    # def update_repos(repo_tuple_array):
    #     ingester = RepoFileIngester()
    #     Ingester.update_repos_using_ingester(ingester, repo_tuple_array)

    # ----------------------------------------------------
    # Instance Initialization
    # ----------------------------------------------------
    def __init__(self,
                 aws_profile='w3hn-admin',
                 bucket='deadmandao',
                 raw_path='web3hackernetwork/data_pipeline/raw'):
        # super().__init__(aws_profile, bucket, raw_path, 'recent_repo')
        # self.log = logger(__file__)
        self.s3_util = S3Util(profile=aws_profile, bucket_name=bucket)
        self.bucket = bucket
        self.raw_path = raw_path
        self.dataset_path = f'{self.raw_path}/recent_repo'

    # ----------------------------------------------------
    # Instance API
    # ----------------------------------------------------

    def create_table(self, recent_repo_json_object):
        code_suffixes = ['.js', '.py', '.c', '.java', '.go', '.ts',
                         '.cpp', '.php', '.rb', '.cs', '.cc', '.rs',
                         '.tsx', '.scala', '.jsx']

        owners = list()
        repo_names = list()
        extensions = list()
        last_updates = list()
        licenses = list()
        num_starss = list()
        num_forkss = list()
        synthetic_keys = list()
        for recent_repo in recent_repo_json_object:
            owner = recent_repo['owner']['login']
            repo_name = recent_repo['name']
            synthetic_key = pq_util.repo_partition_key(owner, repo_name)
            owners.append(owner)
            repo_names.append(repo_name)
            language = recent_repo['language']
            if language == 'Java': language = '.java'
            else: continue
            extensions.append(language)
            date = dateutil.parser.isoparse(recent_repo['pushed_at'])
            last_updates.append(date)
            license = recent_repo['license']
            if not license: license = 'Proprietary'
            else:
                if license['key']: license = license['key']
            licenses.append(license)
            num_starss.append(recent_repo['watchers_count'])
            num_forkss.append(recent_repo['forks_count'])
            synthetic_keys.append(synthetic_key)
        data = [
            owners,
            repo_names,
            extensions,
            last_updates,
            licenses,
            num_starss,
            num_forkss,
            synthetic_keys,
        ]
        batch = pa.RecordBatch.from_arrays(data, RecentRepoIngester.COLUMN_NAMES)
        inferred_table = pa.Table.from_batches([batch])
        explicit_table = inferred_table.cast(RecentRepoIngester.EXPLICIT_SCHEMA)
        return explicit_table

    def write_to_s3(self, table):
        s3fs = self.s3_util.pyarrow_fs()
        # 's3://deadmandao/web3hackernetwork/data_pipeline/published/'
        # out_file = f'./recent_repo.csv'
        # dataset_path = self.dataset_path
        bucket_path = f'{self.s3_util.bucket.name}/{self.dataset_path}'
        if self.s3_util.path_exists(self.dataset_path):
            log.info(f'deleting {bucket_path}')
            s3fs.delete_dir(f'{bucket_path}')
        else:
            log.info(f'no delete at {bucket_path}')
        pq.write_to_dataset(table,
                            root_path=bucket_path,
                            filesystem=s3fs)
    
if __name__ == '__main__':
    ingester = RecentRepoIngester()
    fyle = 'sandbox/data/bob/recent_repo.json'
    fyle = 'sandbox/data/bob/recent_repo_live.json'
    with open(fyle, 'r') as json_file:
        json_obj = json.load(json_file)
        table = ingester.create_table(json_obj)
        ingester.write_to_s3(table)

