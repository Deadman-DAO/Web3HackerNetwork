import dateutil.parser
import pyarrow as pa

import w3hn.hadoop.parquet_util as pq_util
from w3hn.datapipe.ingest.ingester import Ingester

from w3hn.log.log_init import logger
log = logger(__file__)

class BlameIngester(Ingester):

    # ----------------------------------------------------
    # Constants
    # ----------------------------------------------------

    # Unique for each ingester.
    COLUMN_NAMES = [
        'owner', 'repo_name', 'owner_repo', 'file_path',
        'author_name', 'author_email', 'line_count', 'partition_key'
    ]

    # Unique for each ingester.
    EXPLICIT_SCHEMA = pa.schema([
        pa.field("owner", pa.string()),
        pa.field("repo_name", pa.string()),
        pa.field("owner_repo", pa.string()),
        pa.field("file_path", pa.string()),
        pa.field("author_name", pa.string()),
        pa.field("author_email", pa.string()),
        pa.field("line_count", pa.int64()),
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
        ingester = BlameIngester()
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
        super().__init__(aws_profile, bucket, raw_path, 'blame')

    # ----------------------------------------------------
    # Instance API
    # ----------------------------------------------------

    def instance_update_repos(self, repo_tuple_array):
        Ingester.update_repos_using_ingester(this, repo_tuple_array)

    # Unique for each ingester.
    def extract_data(self, owner, repo_name,
                     blame_map=None, dependency_map=None, numstat=None):
        lines = dict()
        for file_path, val in blame_map.items():
            for user_pair, line_count in val.items():
                if '\t' in user_pair:
                    (user_name, user_email) = user_pair.split('\t')
                    user_name = user_name.strip()
                    user_email = user_email.strip()
                    user_email = user_email[1:len(user_email)-1]
                    unique_key = f'{file_path}\t{user_name}\t{user_email}'
                    lines[unique_key] = line_count
                else:
                    log.error(f'cannot split on tab: {owner} {repo_name} "{user_pair}"')
        return lines

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
        batch = pa.RecordBatch.from_arrays(data, BlameIngester.COLUMN_NAMES)
        inferred_table = pa.Table.from_batches([batch])
        explicit_table = inferred_table.cast(BlameIngester.EXPLICIT_SCHEMA)
        return explicit_table
