# ========= External Libraries =================
import bz2
import datetime
import os
import re
import sys
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
# ----------------------------------------------

# ========== Project Root Path =================
this_path = os.path.abspath(sys.path[0])
project_dir = 'Web3HackerNetwork'
w3hndex = this_path.index(project_dir)
root_path = this_path[0:w3hndex + len(project_dir)]
# ---------- Local Library Path ----------------
# sys.path.insert(0, f'{root_path}/python')
# ---------- Local Libraries -------------------
from w3hn.aws.aws_util import S3Util
from w3hn.datapipe.ingest.blame import BlameIngester
from w3hn.datapipe.ingest.dependency import DependencyIngester
from w3hn.datapipe.ingest.file_hacker_commit import FileHackerCommitIngester
from w3hn.datapipe.ingest.repo_file import RepoFileIngester
import w3hn.hadoop.parquet_util as pq_util
import w3hn.log.log_init as log_init
# ----------------------------------------------

class IngesterRunner:
    BLAME_JOB = 1
    DEPS_JOB = 2
    FILE_HACKER_JOB = 4
    REPO_FILE_JOB = 8

    def __init__(self,
                 new_file,
                 old_file = None,
                 test_mode = True,
                 run_blame = False,
                 run_deps = False,
                 run_file_hacker = False,
                 run_repo_file = False,
                 low_partition_limit = '00',
                 high_partition_limit = 'ff'):
        self.log = log_init.logger(__file__)
        self.jobs = 0
        self.new_file = new_file
        self.old_file = old_file
        self.test_mode = test_mode
        if run_blame:
            self.jobs = self.jobs | IngesterRunner.BLAME_JOB
        if run_deps:
            self.jobs = self.jobs | IngesterRunner.DEPS_JOB
        if run_file_hacker:
            self.jobs = self.jobs | IngesterRunner.FILE_HACKER_JOB
        if run_repo_file:
            self.jobs = self.jobs | IngesterRunner.REPO_FILE_JOB
        self.json_s3_util = \
            S3Util(profile="enigmatt", bucket_name='numstat-bucket')
        self.w3hn_s3_util = \
            S3Util(profile='w3hn-admin', bucket_name='deadmandao')
        self.s3_file_metadata_dir = 'web3hackernetwork/metadata/files'
        self.old_s3_ls_key = f'{self.s3_file_metadata_dir}/{old_file}'
        self.new_s3_ls_key = f'{self.s3_file_metadata_dir}/{new_file}'
        self.low_partition_limit = low_partition_limit
        self.high_partition_limit = high_partition_limit

    def diff_s3_list(self, old_lines, new_lines):
        old_lines = set(old_lines)
        diffed_lines = list()
        for line in new_lines:
            if line not in old_lines:
                diffed_lines.append(line)
        return diffed_lines

    def parse_s3_list(self, lines):
        repo_files = dict()
        file_count = 0
        for line in lines:
            if line == '': continue
            line_parts = re.split(' +', line)
            # date = line_parts[0] # time = line_parts[1] # size = line_parts[2]
            path = line_parts[3]
            path_parts = re.split('/', path)
            owner = path_parts[1]
            repo_name = path_parts[2]
            file_type = path_parts[3]
            if file_type == 'blame_map.json.bz2' \
               and not (self.jobs & IngesterRunner.BLAME_JOB): continue
            if file_type == 'dependency_map.json.bz2' \
               and not (self.jobs & IngesterRunner.DEPS_JOB): continue
            if file_type == 'log_numstat.out.json.bz2' \
               and not (self.jobs
                        & (IngesterRunner.FILE_HACKER_JOB \
                           | IngesterRunner.REPO_FILE_JOB)): continue
            partition_key = pq_util.repo_partition_key(owner, repo_name)
            if partition_key >= self.low_partition_limit \
               and partition_key <= self.high_partition_limit:
                key = (partition_key, file_type)
                if key not in repo_files: repo_files[key] = list()
                repo_files[key].append(path)
                file_count += 1
        self.log.info(f'parse_s3_list found {file_count} files with {len(repo_files)} partition/type pairs')
        return repo_files

    def get_update_partitions(self):
        new_lines = self.w3hn_s3_util.get_text_lines_from_bz2(self.new_s3_ls_key)
        repo_files = None
        if self.old_file is not None:
            self.log.info(f'running differential refresh from {self.old_s3_ls_key} and {self.new_s3_ls_key}')
            old_lines = self.w3hn_s3_util.get_text_lines_from_bz2(self.old_s3_ls_key)
            lines = self.diff_s3_list(old_lines, new_lines)
            repo_files = self.parse_s3_list(lines)
        else:
            self.log.info(f'running full refresh from {self.new_s3_ls_key}')
            repo_files = self.parse_s3_list(new_lines)
        return repo_files

    def load_json(self, file_path):
        path_parts = re.split('/', file_path)
        owner = path_parts[1]
        repo_name = path_parts[2]
        file_type = path_parts[3]
        try:
            self.log.debug(f'loading {file_path}')
            json_obj = self.json_s3_util.get_json_obj_at_key(file_path)
            repo_tuple = (owner, repo_name, json_obj, json_obj, json_obj)
            return repo_tuple
        except Exception:
            self.log.exception(f'ERROR reading json {file_path}')
        return None

    def update(self, file_paths, ingesters):
        futures = list()
        with ThreadPoolExecutor(max_workers=10) as fetch_pool:
            threadmap = fetch_pool.map(self.load_json, file_paths)
        repo_tuple_array = list()
        for result in threadmap:
            if result is not None: repo_tuple_array.append(result)
        num_files = len(file_paths)
        for ingester in ingesters:
            type_count_msg = f'{type(ingester)} with {num_files} files'
            if self.test_mode:
                self.log.info(f'TEST_MODE: {type_count_msg}')
            else:
                self.log.info(f'LIVE_MODE: {type_count_msg}')
                try:
                    ingester.instance_update_repos(repo_tuple_array)
                except Exception:
                    self.exception(f'ERROR in {type(ingester)}')

    def multi_phile(self):
        update_partitions = self.get_update_partitions()
        keys = list(update_partitions.keys())
        keys.sort()
        for update_key in keys:
            (partition_key, file_type) = update_key
            file_paths = update_partitions[update_key]
            if file_type == 'blame_map.json.bz2':
                if self.jobs & IngesterRunner.BLAME_JOB:
                    self.log.info(f'loading blame jsons for partition {partition_key}')
                    self.update(file_paths, [BlameIngester()])
            elif file_type == 'dependency_map.json.bz2':
                if self.jobs & IngesterRunner.DEPS_JOB:
                    self.log.info(f'loading dependency jsons for partition {partition_key}')
                    self.update(file_paths, [DependencyIngester()])
            elif file_type == 'log_numstat.out.json.bz2':
                if self.jobs & (IngesterRunner.FILE_HACKER_JOB | IngesterRunner.REPO_FILE_JOB):
                    self.log.info(f'loading numstat jsons for partition {partition_key}')
                    ingesters = list()
                    if self.jobs & IngesterRunner.FILE_HACKER_JOB:
                        ingesters.append(FileHackerCommitIngester())
                    if self.jobs & IngesterRunner.REPO_FILE_JOB:
                        ingesters.append(RepoFileIngester())
                    self.update(file_paths, ingesters)
            else:
                self.log.warn(f'unrecognized file type: {partition_key}, {file_type}, {update_key}, {file_paths}')

if __name__ == '__main__':
    log_init.initialize()
    old_file = 'numstat_bucket_repo_files.5.log.bz2'
    new_file = 'numstat_bucket_repo_files.6.log.bz2'
    low_limit = '00' # '00' for all
    high_limit = '03' # 'ff' for all
    runner = IngesterRunner(
        new_file,
        old_file = old_file,
        test_mode = True,
        low_partition_limit = low_limit,
        high_partition_limit = high_limit,
        run_blame = True,
        run_deps = True,
        run_file_hacker = True,
        run_repo_file = True
    )
    runner.multi_phile()
