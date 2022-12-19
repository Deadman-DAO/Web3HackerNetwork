import dateutil.parser
import pyarrow as pa

import w3hn.hadoop.parquet_util as pq_util
from w3hn.datapipe.ingest.ingester import Ingester

from w3hn.log.log_init import logger
log = logger(__file__)

class RepoInfoIngester(Ingester):

    # ----------------------------------------------------
    # Constants
    # ----------------------------------------------------

    # Unique for each ingester.
    EXPLICIT_SCHEMA = pa.schema([
        pa.field("repo_id", pa.int64()),
        pa.field("repo_name", pa.string()),
        pa.field("owner", pa.string()),
        pa.field("owner_id", pa.int64()),
        pa.field("owner_type", pa.string()),
        pa.field("created_at", pa.timestamp('us', tz='UTC')),
        pa.field("updated_at", pa.timestamp('us', tz='UTC')),
        pa.field("pushed_at", pa.timestamp('us', tz='UTC')),
        pa.field("size", pa.int64()),
        pa.field("stargazers_count", pa.int64()),
        pa.field("watchers_count", pa.int64()),
        pa.field("language", pa.string()),
        pa.field("has_issues", pa.bool_()),
        pa.field("forks_count", pa.int64()),
        pa.field("open_issues_count", pa.int64()),
        pa.field("license_key", pa.string()),
        pa.field("license_name", pa.string()),
        pa.field("license_spdx_id", pa.string()),
        pa.field("license_url", pa.string()),
        pa.field("network_count", pa.int64()),
        pa.field("subscribers_count", pa.int64()),
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
        ingester = RepoInfoIngester()
        Ingester.update_repos_using_ingester(ingester, repo_tuple_array)
    
    # ----------------------------------------------------
    # Instance Initialization
    # ----------------------------------------------------

    # Only the suffix on self.dataset_path changes from one
    # parquet ingester to another.
    def __init__(self,
                 aws_profile='w3hn-admin',
                 bucket='deadmandao',
                 raw_path='web3hackernetwork/data_pipeline/raw'):
        super().__init__(aws_profile, bucket, raw_path, 'repo_info')

    # ----------------------------------------------------
    # Instance API
    # ----------------------------------------------------

    # Unique for each ingester.
    def extract_data(self, owner, repo_name, repo):
        raw_dataset = dict()
        synthetic_key = pq_util.repo_partition_key(owner, repo_name)
        meta = dict()
        meta['repo_id'] = repo['id']
        meta['repo_name'] = repo['name']
        meta['owner'] = repo['owner']['login']
        meta['owner_id'] = repo['owner']['id']
        meta['owner_type'] = repo['owner']['type']
        meta['created_at'] = dateutil.parser.isoparse(repo['created_at'])
        meta['updated_at'] = dateutil.parser.isoparse(repo['updated_at'])
        meta['pushed_at'] = dateutil.parser.isoparse(repo['pushed_at'])
        meta['size'] = repo['size']
        meta['stargazers_count'] = repo['stargazers_count']
        meta['watchers_count'] = repo['watchers_count']
        meta['language'] = repo['language']
        meta['has_issues'] = repo['has_issues']
        meta['forks_count'] = repo['forks_count']
        meta['open_issues_count'] = repo['open_issues_count']
        meta['license_key'] = repo['license']['key']
        meta['license_name'] = repo['license']['name']
        meta['license_spdx_id'] = repo['license']['spdx_id']
        meta['license_url'] = repo['license']['url']
        meta['network_count'] = repo['network_count']
        meta['subscribers_count'] = repo['subscribers_count']
        meta['partition_key'] = synthetic_key
        raw_dataset['/'.join(owner, repo_name)] = meta

        return raw_dataset


    def create_table(self, new_data, owner, repo_name):
        count = len(new_data)
        synthetic_key = pq_util.repo_partition_key(owner, repo_name)
        owners = [owner for i in range(count)]
        repo_names = [repo_name for i in range(count)]
        owner_repos = [f'{owner}\t{repo_name}' for i in range(count)]
        paths = list()
        author_names = list()
        author_emails = list()
        line_counts = list()
        partition_keys = [synthetic_key for i in range(count)]

        for unique_key, line_count in new_data.items():
            (file_path, author_name, author_email) = unique_key.split('\t')
            paths.append(file_path)
            author_names.append(author_name)
            author_emails.append(author_email)
            line_counts.append(line_count)

        data = [
            pa.array(owners), pa.array(repo_names), pa.array(owner_repos),
            pa.array(paths), pa.array(author_names), pa.array(author_emails),
            pa.array(line_counts), pa.array(partition_keys)
        ]
        batch = pa.RecordBatch.from_arrays(data, self.EXPLICIT_SCHEMA.names)
        inferred_table = pa.Table.from_batches([batch])
        explicit_table = inferred_table.cast(self.EXPLICIT_SCHEMA)
        return explicit_table
