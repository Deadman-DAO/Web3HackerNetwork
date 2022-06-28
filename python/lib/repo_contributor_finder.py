import traceback
import json
from datetime import datetime as datingdays
from threading import Lock

import time

from child_process import ChildProcessContainer
from db_dependent_class import DBDependent
from git_hub_client import GitHubClient, fetch_json_value
from monitor import MultiprocessMonitor, timeit


class Contributor:
    def __init__(self, login):
        self.login = login
        self.change_count = 0
        self.start_date = datingdays.now().timestamp()
        self.end_date = 0

    def add_week(self, week_start_timestamp, count):
        self.change_count += count
        if self.start_date > week_start_timestamp:
            self.start_date = week_start_timestamp
        if self.end_date < week_start_timestamp:
            self.end_date = week_start_timestamp


class ContributorFinder(DBDependent, GitHubClient):
    def __init__(self, **kwargs):
        GitHubClient.__init__(self, **kwargs)
        DBDependent.__init__(self, **kwargs)
        self.running = True
        self.success = False
        self.repo_id = -1
        self.repo_owner = None
        self.repo_name = None
        self.url_prefix = 'https://api.github.com/repos/'
        self.url_contributors = '/stats/contributors'
        self.contributors = None
        self.repo_contributor = None
        self.completed_count = 0
        self.monitor = None
        self.fetch_contributor_info_json = None

    def form_repo_url(self):
        return ''.join((self.url_prefix, self.repo_owner, '/', self.repo_name))

    def form_contributors_url(self):
        return ''.join((self.form_repo_url(), self.url_contributors))

    @timeit
    def get_next_repo(self):
        self.success = False
        self.execute_procedure('ReserveRepoToDiscoverContributors', [self.machine_name])
        for goodness in self.get_cursor().stored_results():
            result = goodness.fetchone()
            if result:
                self.repo_id = result[0]
                self.repo_owner = result[1]
                self.repo_name = result[2]
                self.success = True
        return self.success

    @timeit
    def sleepy_time(self):
        time.sleep(60)

    @timeit
    def fetch_contributor_info(self):
        update_database = False
        self.contributors = []
        self.fetch_contributor_info_json = self.fetch_json_with_lock(self.form_contributors_url())
        if self.fetch_contributor_info_json is None:
            if self.html_reply.status_code == 202:
                self.delay_repo_processing(self.repo_id)
            elif self.html_reply.status_code == 404:
                print('That repo is unreachable', self.form_contributors_url())
                update_database = True
            else:
                raise StopIteration('Restful Response did not form a parseable JSON document', self.form_contributors_url())
        else:
            update_database = True
            for contributor in self.fetch_contributor_info_json:
                # JSON doc is an array of "contributor" objects
                author_elem = fetch_json_value('author', contributor)
                author = fetch_json_value('login', author_elem)
                c = Contributor(author)
                self.contributors.append(c)
                weeks = fetch_json_value('weeks', contributor)
                for w in weeks:
                    ts = fetch_json_value('w', w)
                    added = fetch_json_value('a', w)
                    deleted = fetch_json_value('d', w)
                    ttl = added-deleted
                    if ttl > 0:
                        c.add_week(ts, ttl)
        return update_database

    @timeit
    def update_database(self):
        self.execute_procedure('AddContributors',
                                   [self.repo_id, json.dumps(self.contributors,
                                                             default=lambda o: o.__dict__,
                                                             sort_keys=True, indent=2)])
        self.completed_count += 1

    def get_completed_count(self):
        return self.completed_count

    @timeit
    def error_sleep(self):
        self.close_cursor()
        time.sleep(60)

    def main(self):
        self.monitor = MultiprocessMonitor(web_lock=self.web_lock, cont=self.get_completed_count, cin=self.get_stats)

        while self.running:
            try:
                if self.get_next_repo():
                    try:
                        if self.fetch_contributor_info():
                            self.update_database()
                    except Exception as si:
                        print("Error encountered in ContributorFinder MAIN", si)
                        self.error_sleep()
                else:
                    self.sleepy_time()
            except Exception as anything:
                print(anything)
                traceback.print_exc()
                self.error_sleep()


if __name__ == "__main__":
    _lock = Lock()
    ChildProcessContainer(ContributorFinder(web_lock=_lock), 'cf1').join()
