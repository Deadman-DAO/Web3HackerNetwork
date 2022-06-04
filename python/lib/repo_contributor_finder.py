from datetime import datetime as datingdays
from db_dependent_class import DBDependent
from git_hub_client import GitHubClient, fetch_json_value
from monitor import MultiprocessMonitor, timeit
import time
import json
from threading import Lock
from child_process import ChildProcessContainer


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
    def __init__(self, lock):
        GitHubClient.__init__(self, lock)
        DBDependent.__init__(self)
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
        self.get_cursor().callproc('ReserveRepoToDiscoverContributors', [self.machine_name])
        result = self.cursor.fetchone()
        if result is not None:
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
        self.fetch_contributor_info_json = self.fetch_json_with_lock(self.form_contributors_url())
        if self.fetch_contributor_info_json is None:
            raise StopIteration('Restful Response did not form a parseable JSON document', self.form_contributors_url())
        self.contributors = []
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
                changed = fetch_json_value('c', w)
                ttl = added+deleted+changed
                if ttl > 0:
                    c.add_week(ts, ttl)

    @timeit
    def update_database(self):
        self.get_cursor().callproc('AddContributors',
                                   [self.repo_id, json.dumps(self.contributors,
                                                             default=lambda o: o.__dict__,
                                                             sort_keys=True, indent=2)])
        self.completed_count += 1

    def get_completed_count(self):
        return self.completed_count

    @timeit
    def error_sleep(self):
        time.sleep(60)

    def main(self):
        self.monitor = MultiprocessMonitor(self.git_hub_lock, cont=self.get_completed_count, cin=self.get_stats)

        while self.running:
            if self.get_next_repo():
                try:
                    self.fetch_contributor_info()
                    self.update_database()
                except StopIteration as si:
                    print("Error encountered in ContributorFinder MAIN", si)
                    self.error_sleep()
            else:
                self.sleepy_time()


if __name__ == "__main__":
    _lock = Lock()
    ChildProcessContainer(ContributorFinder(_lock), 'cf1').join()
