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
        pa.field("owner", pa.string()),
        pa.field("repo_name", pa.string()),
        pa.field("owner_repo", pa.string()),
        pa.field("repo_id", pa.int64()),
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
                 bucket='deadmandao'):
        super().__init__(aws_profile, bucket, 'repo_info',
                         sort_by=[('owner', 'ascending'), ('repo_name', 'ascending')])

    # ----------------------------------------------------
    # Instance API
    # ----------------------------------------------------

    # Unique for each ingester.
    def extract_data(self, owner, repo_name, repo):
        raw_dataset = dict()
        synthetic_key = pq_util.repo_partition_key(owner, repo_name)
        meta = dict()
        meta['owner'] = repo['owner']['login'] if repo['owner'] else None
        meta['repo_name'] = repo['name']
        meta['repo_id'] = repo['id']
        meta['owner_id'] = repo['owner']['id'] if repo['owner'] else None
        meta['owner_type'] = repo['owner']['type'] if repo['owner'] else None
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
        meta['license_key'] = repo['license']['key'] if repo['license'] else None
        meta['license_name'] = repo['license']['name'] if repo['license'] else None
        meta['license_spdx_id'] = repo['license']['spdx_id'] if repo['license'] else None
        meta['license_url'] = repo['license']['url'] if repo['license'] else None
        meta['network_count'] = repo['network_count']
        meta['subscribers_count'] = repo['subscribers_count']
        meta['partition_key'] = synthetic_key
        #raw_dataset['/'.join((owner, repo_name))] = meta

        return meta


    def create_table(self, new_data, owner, repo_name):
        synthetic_key = pq_util.repo_partition_key(owner, repo_name)
        owners = [owner]
        repo_names = [repo_name]
        owner_repos = [f'{owner}/{repo_name}']
        repo_ids = [new_data['repo_id']]
        owner_ids = [new_data['owner_id']]
        owner_types = [new_data['owner_type']]
        created_ats = [new_data['created_at']]
        updated_ats = [new_data['updated_at']]
        pushed_ats = [new_data['pushed_at']]
        sizes = [new_data['size']]
        stargazers_counts = [new_data['stargazers_count']]
        watchers_counts = [new_data['watchers_count']]
        languages = [new_data['language']]
        has_issuess = [new_data['has_issues']]
        forks_counts = [new_data['forks_count']]
        open_issues_counts = [new_data['open_issues_count']]
        license_keys = [new_data['license_key']]
        license_names = [new_data['license_name']]
        license_spdx_ids = [new_data['license_spdx_id']]
        license_urls = [new_data['license_url']]
        network_counts = [new_data['network_count']]
        subscribers_counts = [new_data['subscribers_count']]
        partition_keys = [synthetic_key]

        data = [
            pa.array(owners), pa.array(repo_names), pa.array(owner_repos),
            pa.array(repo_ids), pa.array(owner_ids), pa.array(owner_types),
            pa.array(created_ats), pa.array(updated_ats), pa.array(pushed_ats),
            pa.array(sizes), pa.array(stargazers_counts), pa.array(watchers_counts),
            pa.array(languages), pa.array(has_issuess), pa.array(forks_counts),
            pa.array(open_issues_counts), pa.array(license_keys), pa.array(license_names),
            pa.array(license_spdx_ids), pa.array(license_urls), pa.array(network_counts),
            pa.array(subscribers_counts), pa.array(partition_keys)
        ]
        batch = pa.RecordBatch.from_arrays(data, self.EXPLICIT_SCHEMA.names)
        inferred_table = pa.Table.from_batches([batch])
        explicit_table = inferred_table.cast(self.EXPLICIT_SCHEMA)
        return explicit_table
