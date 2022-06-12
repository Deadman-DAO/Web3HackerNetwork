import sys
import os
import json
import time
from socket import gethostname
from db_dependent_class import DBDependent
from monitor import MultiprocessMonitor, timeit
from threading import Lock
from git_hub_client import GitHubClient


def format_id_check_url(repo_owner, repo_name, commit_hash):
    return 'https://api.github.com/repos/'+repo_owner+'/'+repo_name+'/commits/'+commit_hash


class GitHubUserIDFinder(DBDependent, GitHubClient):

    def __init__(self, **kwargs):
        GitHubClient.__init__(self, **kwargs)
        DBDependent.__init__(self, **kwargs)
        self.kwargs = kwargs
        self.machine_name = os.uname().nodename if sys.platform != "win32" else gethostname()
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
            self.execute_procedure('ReserveNextUnresolvedAlias', [self.machine_name])
            for goodness in self.get_cursor().stored_results():
                result = goodness.fetchone()
                if result:
                    self.author_info = json.loads(result[0])
                    rslt = self.author_info
        except Exception as e:
            print('Error occurred calling ReserveNextUnresolvedAlias', e)
        return rslt

    @timeit
    def no_work_sleep(self):
        time.sleep(60)

    @timeit
    def call_resolve_sql_proc(self, author_id, github_user_id):
        try:
            self.execute_procedure('ResolveAliasViaPrimaryKey', (author_id, github_user_id))
        except Exception as e:
            print('Error encountered calling ResolveAliasViaPrimaryKey', e)

    @timeit
    def resolve_it(self):
        alias_not_found = True
        idx = 0
        author_id = self.author_info[idx]['alias_id']
        while alias_not_found and idx < len(self.author_info):
            url = format_id_check_url(self.author_info[idx]['owner'],
                                      self.author_info[idx]['name'],
                                      self.author_info[idx]['commit_id'])
            _json = self.fetch_json_with_lock(url)
            if _json:
                commit_details_block = _json['author']
                if commit_details_block is not None and 'login' in commit_details_block.keys():
                    self.call_resolve_sql_proc(author_id, commit_details_block['login'])
                    self.try_counters[idx] += 1
                    alias_not_found = False
            else:
                print('Empty JSON block returned from', url)
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
        m = MultiprocessMonitor(web_lock=self.web_lock, my=self.get_stats)
        while self.running:
            if self.reserve_next_author() is None:
                self.no_work_sleep()
            else:
                self.resolve_it()


if __name__ == "__main__":
    GitHubUserIDFinder(web_lock=Lock()).main()

