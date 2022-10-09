import random
from time import sleep
from utils import md5_hash
import pyarrow as pa
import pyarrow.parquet as pq
import boto3
import bz2
import json
import sys
local_lib_dir = '../sandbox/python/matt/'
sys.path.append(local_lib_dir)

from repo_grabber import RepoGrabber


entry = [{'Date': {'type': pa.string}},
         {'commit': {'type': pa.string, 'label': 'commit_id'}},
         {'Author': {'type': pa.string, 'label': 'author_hash', 'method': md5_hash}},
         {'orig_timezone': {'type': pa.string, 'label': 'tz'}},
         {'file_list':
              {'type': 'key_val',
               'key': 'file_name',
               'field_array': [{'file_name': {'type': pa.string, 'label': 'file_path'}},
                               {'binary': {'type': pa.bool_}},
                               {'inserts': {'type': pa.int64}},
                               {'deletes': {'type': pa.int64}}
                              ]
              }
         }]


def process_item( item, object_entry_point ):
    for key in item.keys():
        obj = item[key]
        if callable(obj['type']):
            # Simple single item
            if 'data' not in obj:
                obj['data'] = []
            if key in object_entry_point:
                obj['data'].append(object_entry_point[key])
            else:
                print('Missing key: '+key)
        else:
            sub_key = obj['key']
            field_array = obj['field_array']
            process_item(obj, object_entry_point[key])


def execute_analysis(owner=None, repo_name=None, numstat=None, repo_path=None):
    clone = list(entry)
    for commit in numstat:
        for item in clone:
            process_item(item, commit)


if __name__ == '__main__':
    owner = 'apache'
    repo = 'ant'
    numstat = RepoGrabber().get_numstat(owner, repo)
    execute_analysis(owner=owner, repo_name=repo, numstat=numstat)