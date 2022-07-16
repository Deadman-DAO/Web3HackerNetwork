import sys
import os
import time
from monitor import timeit
from monitor import mem_info
from socket import gethostname
from datetime import datetime as datingdays, timedelta
import iso_date_parser
from pytz import timezone
from threading import Lock
from git_hub_client import GitHubClient, fetch_json_value
from db_driven_task import DBDrivenTaskProcessor, DBTask

AZ = timezone('US/Arizona')
MIN_DATE = datingdays.now(AZ)
MAX_DATE = datingdays.fromtimestamp(0, AZ)


class RepoCounter:
    def __init__(self):
        self.commit_count = 0
        self.min_date = MIN_DATE
        self.max_date = MAX_DATE
        self.owner = None
        self.name = None


class AuthorCommitHistoryProcessor(DBDrivenTaskProcessor, GitHubClient, DBTask):

    class PostProcess(DBTask):
        def __init__(self, mom):
            self.mom = mom

        def get_proc_name(self):
            return 'releaseAlias'

        def get_proc_parameters(self):
            return [self.mom.alias_hash, self.mom.author_commit_count]

        def process_db_results(self, result_args):
            pass

    def get_proc_name(self):
        return self.reserve_next_user_proc

    def get_proc_parameters(self):
        return [self.machine_name]

    def process_db_results(self, result_args):
        result = None
        for goodness in self.get_cursor().stored_results():
            result = goodness.fetchone()
            if result:
                self.user_id = result[0]
                self.alias_hash = result[1]
        return result

    def get_job_fetching_task(self):
        return self

    def get_job_completion_task(self):
        return self.post_processor

    def process_task(self):
        self.repo_map = {}
        self.process_author()
        for counter in self.repo_map.values():
            self.call_update_repo(counter)

    def __init__(self, **kwargs):
        GitHubClient.__init__(self, **kwargs)
        DBDrivenTaskProcessor.__init__(self, **kwargs)
        self.max_call_count = 6
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
        self.add_update_repo_proc = 'addUpdateRepo'
        self.reserve_next_user_proc = 'reserveNextUser'
        self.post_processor = self.PostProcess(self)
        self.author_commit_count = 0
        self.repo_map = None
        with open('./web3.github.token', 'r') as f:
            self.token = f.readline()
            self.token = self.token.strip('\n')
            self.headers = {'Authorization': 'token %s' % self.token}

    def get_total_count(self):
        return self.total_count

    def format_user_url(self, user_id):
        var = self.urlPrefix + "?q=author:" + user_id + '+author-date:<' + self.startDate.isoformat() + \
              '&sort=author-date&order=desc&per_page=100&page=1'
        return var

    def get_cur_job(self):
        return self.user_id if self.user_id is not None else 'None'

    def init(self):
        self.monitor.single.add_display_methods(mem=mem_info,
                                         curjob=self.get_cur_job,
                                         callcnt=self.get_call_count,
                                         cmt_cnt=self.get_total_count,
                                         x=self.get_stats)

    def get_call_count(self):
        return self.call_count

    @timeit
    def sleep_n_load(self):
        time.sleep(1)
        # print(self.format_user_url(self.user_id))
        body = self.fetch_json_with_lock(self.format_user_url(self.user_id))
        return body

    @timeit
    def evaluate_document(self):
        cont_inue = True
        stop_looping = False

        if self.body is None:
            print('Unable to load JSON')
            cont_inue = False
            stop_looping = True
        else:
            self.total_count = self.body['total_count']
            if self.author_commit_count < 1:
                self.author_commit_count = self.total_count
            if self.total_count == self.last_count:
                print('Identical result set found.  Moving on.', self.total_count, self.last_count)
                stop_looping = True
                cont_inue = False
            self.last_count = self.total_count
            self.incomplete_results = self.body['incomplete_results']
            self.array = self.body['items']
            if self.array is None or len(self.array) < 1:
                stop_looping = True
                cont_inue = False
        return cont_inue, stop_looping

    def reset_last_date(self):
        self.startDate = datingdays.now(timezone('US/Arizona'))

    @timeit
    def call_update_repo(self, counter):
        self.execute_procedure(self.add_update_repo_proc,
           (counter.owner, counter.name, counter.min_date, counter.max_date, counter.commit_count))

    @timeit
    def process_author(self):
        done = False
        self.last_count = -1
        self.reset_last_date()
        self.author_commit_count = -1
        call_count = 0

        while not done and call_count < self.max_call_count:
            call_count += 1
            self.body = self.sleep_n_load()
            cont_inue, done = self.evaluate_document()
            if cont_inue:
                for n in self.array:
                    commit = n['commit']
                    com_auth = commit['author']
                    commit_date, orig_time_zone = iso_date_parser.parse(com_auth['date'])
                    self.startDate, orig_time_zone = iso_date_parser.parse(com_auth['date'], tz='US/Arizona')
                    ''' Skip a bit brother - move back in time 30 days and take another 100 samples '''
                    self.startDate = self.startDate - timedelta(days=30)
                    repo = n['repository']
                    repo_name = repo['name']
                    repo_owner = repo['owner']
                    owner_login = repo_owner['login']
                    key = repo_name+':'+owner_login
                    if key not in self.repo_map:
                        self.repo_map[key] = RepoCounter()
                    counter = self.repo_map[key]
                    counter.commit_count += 1
                    counter.min_date = commit_date if commit_date < counter.min_date else counter.min_date
                    counter.max_date = commit_date if commit_date > counter.max_date else counter.max_date
                    counter.owner = owner_login
                    counter.name = repo_name

                if self.total_count < 100 and not self.incomplete_results:
                    done = True


if __name__ == "__main__":
    AuthorCommitHistoryProcessor(web_lock=Lock()).main()
