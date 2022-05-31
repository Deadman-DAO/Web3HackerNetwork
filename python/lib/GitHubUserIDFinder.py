import sys
import os
import json
import requests
import time
import multiprocessing
from socket import gethostname
from db_dependent_class import DBDependent
from monitor import MultiprocessMonitor, timeit


def format_id_check_url(repo_owner, repo_name, commit_hash):
    return 'https://api.github.com/repos/'+repo_owner+'/'+repo_name+'/commits/'+commit_hash


class GitHubUserIDFinder(DBDependent):

    def __init__(self, git_lock):
        super().__init__()
        self.git_lock = git_lock
        self.machine_name = os.uname().nodename if sys.platform != "win32" else gethostname()
        self.get_cursor()
        self.commit_set = None
        self.running = True
        self.call_count = 0
        self.alias_count = 0
        self.fail_count = 0
        self.try_counters = [0, 0, 0]
        self.author_info = None
        self.MAX_LOOPS = 5
        self.good_status_code_count = 0
        self.overload_count = 0
        self.error_count = 0
        with open('./web3.github.token', 'r') as f:
            self.token = f.readline()
            self.token = self.token.strip('\n')
            self.headers = {'Authorization': 'token %s' % self.token}

    def get_call_count(self):
        return self.call_count

    @timeit
    def reserve_next_author(self):
        rslt = None
        try:
            self.cursor.callproc('ReserveNextUnresolvedAlias', (self.machine_name, None))
            result_set = self.cursor.fetchone()
            if result_set is not None and len(result_set) > 0:
                self.author_info = json.loads(result_set[0])
                rslt = self.author_info
        except Exception as e:
            print('Error occurred calling ReserveNextUnresolvedAlias', e)
        return rslt

    @timeit
    def no_work_sleep(self):
        time.sleep(60)


    @timeit
    def retrieve_commit(self, author, repo_owner, repo_name, commit_hash, recurse_count=0):
        reply = None
        try:
            url = format_id_check_url(repo_owner, repo_name, commit_hash)
        except TypeError as te:
            print('Error forming fetch commit URL', author, repo_owner, repo_name, commit_hash, te)
            return reply

        self.git_lock.acquire()
        try:
            time.sleep(1)  # wait a sec
            self.call_count += 1
            reply = requests.get(url, headers=self.headers)
        finally:
            self.git_lock.release()
        if reply is None:
            self.error_count += 1
            print('No response received from API call to GitHub', author, repo_owner, repo_name, commit_hash, recurse_count)
        elif reply.status_code == 422:
            self.error_count += 1
            print('ERROR - Status code:', resp.status_code, 'encountered ', url)
            reply = None
        elif reply.status_code == 403:
            self.overload_count += 1
            # We've exceed our 5000 calls per hour!
            print('Maximum calls/hour exceeded! Sleeping', recurse_count, 'minute(s)')
            print('Working on', commit_hash)
            time.sleep(60*recurse_count)
            if recurse_count <= self.MAX_LOOPS:
                reply = self.retrieve_commit(author, repo_owner, repo_name, commit_hash, recurse_count+1)
            else:
                reply = None
        elif reply.status_code == 200:
            self.good_status_code_count += 1
        else:
            reply = None
        return reply

    @timeit
    def call_resolve_sql_proc(self, author_id, github_user_id):
        try:
            self.cursor.callproc('ResolveAliasViaPrimaryKey', (author_id, github_user_id))
        except Exception as e:
            print('Error encountered calling ResolveAliasViaPrimaryKey', e)

    @timeit
    def resolve_it(self):
        alias_not_found = True
        idx = 0
        author_id = self.author_info[idx]['alias_id']
        while alias_not_found and idx < len(self.author_info):
            info = self.retrieve_commit(author_id,
                                        self.author_info[idx]['owner'],
                                        self.author_info[idx]['name'],
                                        self.author_info[idx]['commit_id'])
            if info is not None:
                j = info.json()
                commit_details_block = j['author']
                if commit_details_block is not None and 'login' in commit_details_block.keys():
                    committer = commit_details_block['login']
                    self.call_resolve_sql_proc(author_id, committer)
                    self.try_counters[idx] += 1
                    alias_not_found = False
            idx += 1
        if alias_not_found:
            self.fail_count += 1
            self.call_resolve_sql_proc(author_id, '<UNABLE_TO_RESOLVE>')

    def get_fail_count(self):
        return self.fail_count

    def get_cur_author(self):
        rv = ''
        if self.author_info is not None:
            rv = self.author_info[0]['alias_id']
        return rv

    def main(self):
        m = MultiprocessMonitor(self.git_lock,
                                gh_cc=self.get_call_count,
                                gh_ca=self.get_cur_author,
                                gh_fc=self.get_fail_count)
        while self.running:
            if self.reserve_next_author() is None:
                self.no_work_sleep()
            else:
                self.resolve_it()


if __name__ == "__main__":
    GitHubUserIDFinder(multiprocessing.RLock()).main()
