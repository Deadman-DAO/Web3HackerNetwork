# ========= External Libraries =================
import datetime
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
# ----------------------------------------------

# ========== Project Root Path =================
this_path = os.path.abspath(sys.path[0])
project_dir = 'Web3HackerNetwork'
w3hndex = this_path.index(project_dir)
root_path = this_path[0:w3hndex + len(project_dir)]
# ---------- Local Library Path ----------------
sys.path.insert(0, f'{root_path}/python')
# ---------- Local Libraries -------------------
# from w3hn.datapipe.ingest.file_hacker_commit import FileHackerCommitIngester
# from w3hn.datapipe.ingest.repo_file import RepoFileIngester
from w3hn.aws.aws_util import S3Util
# import w3hn.hadoop.parquet_util as pq_util
# ----------------------------------------------

s3_util = S3Util(bucket_name='deadmandao', profile='w3hn-admin')
s3_util.delete_recursive('tmp/delete/test')

