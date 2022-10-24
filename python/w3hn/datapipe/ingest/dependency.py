import dateutil.parser
import pyarrow as pa

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
    def update_repos(repo_tuple_array):
        ingester = DependencyIngester()
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
        super().__init__(aws_profile, bucket, raw_path, 'dependency')

    # ----------------------------------------------------
    # Instance API
    # ----------------------------------------------------

    # Unique for each ingester.
    def extract_data(self, owner, repo_name,
                     blame_map=None, dependency_map=None, numstat=None):
        deps_set = set()
        for file_path, libs in dependency_map.items():
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
