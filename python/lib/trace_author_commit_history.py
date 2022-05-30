import sys
import os
import time
import json
from db_dependent_class import DBDependent
from monitor import Monitor
from monitor import timeit
from monitor import mem_info
from socket import gethostname
from datetime import datetime as datingdays
import iso_date_parser
from pytz import timezone
import requests


class AuthorCommitHistoryProcessor(DBDependent):
    def __init__(self):
        super().__init__()
        self.get_cursor()
        self.repo_counter = {}
        self.call_count = 0
        self.running = True
        self.owner = {}
        self.user_id = ''
        self.alias_hash = ''
        self.last_count = -1
        self.total_count = 0
        self.body = None
        self.incomplete_results = False
        self.array = None
        self.machine_name = os.uname().nodename if sys.platform != "win32" else gethostname()
        self.urlPrefix = 'https://api.github.com/search/commits'
        self.startDate = datingdays.now(timezone('UTC'))
        self.add_update_repo_proc = 'w3hacknet.addUpdateRepo'
        self.reserve_next_user_proc = 'w3hacknet.reserveNextUser'
        with open('./web3.github.token', 'r') as f:
            self.token = f.readline()
            self.token = self.token.strip('\n')
            self.headers = {'Authorization': 'token %s' % self.token}

    def get_total_count(self):
        return self.total_count

    def format_user_url(self, user_id):
        var = self.urlPrefix+"?q=author:"+user_id+'+author-date:<'+self.startDate.isoformat()+'&sort=author-date&order=desc&per_page=100&page=1'
        return var

    def load_hacker_url(self, user_id, recurse_count=1):
        ret_val = None
        resp = requests.get(self.format_user_url(user_id), headers=self.headers)
        if resp.status_code == 200:
            time.sleep(1)
            ret_val = resp.json()
        elif resp.status_code == 403:
            print('Rate limit EXCEEDED.  Sleeping for a bit. (recursive_count=', recurse_count,')')
            time.sleep(recurse_count * 60)
            ret_val = self.load_hacker_url(user_id, recurse_count+1)
        else:
            print('Status code returned:', resp.status_code)
            req_headers = resp.request.headers
            for n in req_headers.keys():
                print('\t', n, req_headers[n])
            print(json.dumps(resp.json(), indent=2))
        return ret_val

    @timeit
    def reserve_next_user(self):
        self.cursor.callproc(self.reserve_next_user_proc,
                        (self.machine_name, None, None))
        if self.cursor.sp_outparams:
            tup = self.cursor.fetchone()
            self.user_id = tup[0]
            self.alias_hash = tup[1]
        else:
            self.user_id = None
            self.alias_hash = None

    def get_cur_job(self):
        return self.user_id if self.user_id is not None else 'None'

    @timeit
    def play_dead(self, msg, n_sec):
        print(msg)
        time.sleep(n_sec)

    def main(self):
        self.running = True
        m = Monitor(
            frequency=10,
            mem=mem_info,
            curjob=self.get_cur_job,
            callcnt=self.get_call_count,
            cmt_cnt=self.get_total_count)
        while self.running:
            self.reserve_next_user()
            if self.user_id is None:
                self.play_dead('No work today, sleeping', 60)
            else:
                self.process_author()

    def get_call_count(self):
        return self.call_count

    @timeit
    def sleep_n_load(self):
        time.sleep(2)  # Don't over stay our welcome - Can't exceed 3600/hr, let alone 5000
        body = self.load_hacker_url(self.user_id)
        self.call_count += 1
        if self.call_count % 25 == 0:
            print(self.call_count, 'rest API calls made')
        return body

    def evaluate_document(self):
        cont_inue = True
        stop_looping = False

        self.total_count = self.body['total_count']
        if self.body is None:
            print('Unable to load JSON')
            cont_inue = False
            stop_looping = True
        else:
            if self.total_count == self.last_count:
                print('Identical result set found.  Moving on.', self.total_count, self.last_count)
                stop_looping = True
                cont_inue = False
            self.last_count = self.total_count
            if self.total_count > 20000:
                print('Yikes!', self.total_count, ' seems like a few too many')
                stop_looping = True
            self.incomplete_results = self.body['incomplete_results']
            self.array = self.body['items']
            if self.array is None or len(self.array) < 1:
                stop_looping = True
                cont_inue = False
        return cont_inue, stop_looping

    def reset_last_date(self):
        self.startDate = datingdays.now(timezone('US/Arizona'))

    @timeit
    def call_update_repo(self, owner_login, repo_name, commit_date, orig_time_zone, commit_hash, author_hash):
        self.cursor.callproc(self.add_update_repo_proc, (
            owner_login, repo_name, commit_date, orig_time_zone, commit_hash, author_hash)
        )

    @timeit
    def process_author(self):
        done = False
        self.last_count = -1
        self.reset_last_date()

        while not done:
            self.body = self.sleep_n_load()
            cont_inue, done = self.evaluate_document()
            if cont_inue:
                for n in self.array:
                    commit = n['commit']
                    com_auth = commit['author']
                    commit_date, orig_time_zone = iso_date_parser.parse(com_auth['date'])
                    self.startDate, orig_time_zone = iso_date_parser.parse(com_auth['date'], tz='US/Arizona')
                    repo = n['repository']
                    repo_name = repo['name']
                    repo_owner = repo['owner']
                    owner_login = repo_owner['login']
                    self.call_update_repo(owner_login, repo_name,
                                          commit_date, orig_time_zone,
                                          n['sha'], self.alias_hash)

                if self.total_count < 100 and self.incomplete_results == False:
                    done = True


def main():
    AuthorCommitHistoryProcessor().main()


if __name__ == "__main__":
    main()
