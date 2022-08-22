import threading
import sys
import os
import json
import traceback
from socket import gethostname
from db_dependent_class import DBDependent
from monitor import MultiprocessMonitor, timeit
from threading import Lock
from git_hub_client import GitHubClient


def no_none(val):
    return val if val is not None else 'None'


def format_id_check_url(repo_owner, repo_name, commit_hash):
    if repo_owner is None or repo_name is None or commit_hash is None:
        raise Exception('Bad parameter to format_id_check_url: repo_owner = '+no_none(repo_owner)+' repo_name = '+
                        no_none(repo_name)+' commit_hash = '+no_none(commit_hash))
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
        self.error_wait = int(kwargs['error_wait']) if 'error_wait' in kwargs else 60
        self.interrupt_event = threading.Event()
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
        self.close_cursor()
        self.interrupt_event.wait(self.error_wait)

    @timeit
    def error_sleep(self):
        self.close_cursor()
        self.interrupt_event.wait(self.error_wait)

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
            owner = self.author_info[idx]['owner']
            name = self.author_info[idx]['name']
            hashish = self.author_info[idx]['commit_id']
            if owner is not None and name is not None and hashish is not None:
                url = format_id_check_url(owner,
                                          name,
                                          hashish)
                _json = self.fetch_json_with_lock(url)
                if _json:
                    item = _json
                    try:
                        if 'author' in item:
                            github_user_id = None
                            if item['author'] is None:
                                if ('commit' in item and
                                        item['commit'] is not None and
                                        'author' in item['commit'] and
                                        item['commit']['author'] is not None and
                                        item['commit']['author']['name'] is not None):
                                    github_user_id = item['commit']['author']['login']
                            else:
                                github_user_id = item['author']['login']
                            if github_user_id is not None:
                                self.call_resolve_sql_proc(author_id, github_user_id)
                                self.try_counters[idx] += 1
                                alias_not_found = False
                    except Exception as e:
                        print(e, json.dumps(item))
                else:
                    print('Empty JSON block returned from', url)
                idx += 1
            else:
                print('GitHubUserIDFinder Skipping this one: '+no_none(owner)+','+no_none(name)+','+no_none(hashish))
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
        m = MultiprocessMonitor(web_lock=self.web_lock, my=self.get_stats, cur_alias_pk=self.get_cur_author)
        while self.running:
            try:
                if self.reserve_next_author() is None:
                    self.no_work_sleep()
                else:
                    self.resolve_it()
            except Exception as anything:
                print(anything)
                traceback.print_exc()
                self.error_sleep()


if __name__ == "__main__":
    GitHubUserIDFinder(web_lock=Lock()).main()

