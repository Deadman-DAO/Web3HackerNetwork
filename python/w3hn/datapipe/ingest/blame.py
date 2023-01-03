import dateutil.parser
from enum import Enum
import pyarrow as pa

import w3hn.hadoop.parquet_util as pq_util
from w3hn.datapipe.ingest.ingester import Ingester

from w3hn.log.log_init import logger
log = logger(__file__)

# {
#   "DlitheTournaments/src/main/java/sports/dlithe/tournaments/DlitheTournaments/DlitheTournamentsApplication.java": {
#     "pavanpoojary {pavanpoojary17@gmail.com}": {
#       "author_hash_map": {
#         "2ccdd48f210622d342ae5dbe2d8dab157fecf237": {
#           "epoch": 1643614491,
#           "lines": 13,
#           "time_zone": "+0530"
#         }
#       },
#       "commit_hash_map": {
#         "2ccdd48f210622d342ae5dbe2d8dab157fecf237": {
#           "epoch": 1643614491,
#           "lines": 13,
#           "time_zone": "+0530"
#         }
#       }
#     }
#   },

def add_col(cols, name, tipe, data):
    cols[0].append(name)
    cols[1].append(pa.array(data, tipe))

class BlameIngester(Ingester):

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
                 bucket='deadmandao'):
        super().__init__(aws_profile, bucket, 'blame')

    # ----------------------------------------------------
    # Instance API
    # ----------------------------------------------------

    # Unique for each ingester.
    def extract_data(self, owner, repo_name, json_object):
        cols = dict()
        cols['file_path'] = list()
        cols['author'] = list()
        cols['blame_type'] = list()
        cols['commit_id'] = list()
        cols['epoch'] = list()
        cols['lines'] = list()
        cols['time_zone'] = list()
        for file_path, file_dict in json_object.items():
            for author, author_dict in file_dict.items():
                for blame_type, blame_type_dict in author_dict.items():
                    if blame_type == 'commit_hash_map': continue
                    for commit_id, commit_id_dict in blame_type_dict.items():
                        cols['file_path'].append(file_path)
                        cols['author'].append(author)
                        cols['blame_type'].append(blame_type)
                        cols['commit_id'].append(commit_id)
                        cols['epoch'].append(commit_id_dict['epoch'])
                        cols['lines'].append(commit_id_dict['lines'])
                        cols['time_zone'].append(commit_id_dict['time_zone'])
        return cols

    def create_table(self, new_data, owner, repo_name):
        count = len(new_data['file_path'])
        owner_repo = pq_util.owner_repo(owner, repo_name)
        partition_key = pq_util.repo_partition_key(owner, repo_name)

        tb_names = list()
        tb_data = list()
        cols = (tb_names, tb_data)

        add_col(cols, 'owner', pa.string(), [owner for i in range(count)])
        add_col(cols, 'repo_name', pa.string(), [repo_name for i in range(count)])
        add_col(cols, 'owner_repo', pa.string(), [owner_repo for i in range(count)])
        add_col(cols, 'file_path', pa.string(), new_data['file_path'])
        add_col(cols, 'author', pa.string(), new_data['author'])
        add_col(cols, 'blame_type', pa.string(), new_data['blame_type'])
        add_col(cols, 'commit_id', pa.string(), new_data['commit_id'])
        add_col(cols, 'epoch', pa.int64(), new_data['epoch'])
        add_col(cols, 'lines', pa.int32(), new_data['lines'])
        add_col(cols, 'time_zone', pa.string(), new_data['time_zone'])
        add_col(cols, 'partition_key', pa.string(), [partition_key for i in range(count)])

        batch = pa.RecordBatch.from_arrays(tb_data, tb_names)
        table = pa.Table.from_batches([batch])
        return table
