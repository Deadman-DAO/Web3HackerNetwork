from child_process import ChildProcessContainer

from db_dependent_class import DBDependent
from git_hub_client import fetch_json_value, GitHubClient
from monitor import MultiprocessMonitor, timeit
from repo_contributor_finder import Contributor
from threading import Lock
import iso_date_parser
import time


class Investigator(DBDependent, GitHubClient):
    def __init__(self, lock):
        GitHubClient.__init__(self, lock)
        DBDependent.__init__(self)
        self.repo_last_year = None
        self.url_prefix = 'https://api.github.com/repos/'
        self.url_activity = '/stats/commit_activity'
        self.repo_owner = ''
        self.repo_name = ''
        self.created_at = None
        self.updated_at = None
        self.pushed_at = None
        self.homepage = None
        self.size = None
        self.watchers_count = None
        self.forks_count = None
        self.network_count = None
        self.subscribers_count = None
        self.fetch_repo_info_json = None
        self.fetch_activity_info_json = None

    def form_repo_url(self):
        return ''.join((self.url_prefix, self.repo_owner, '/', self.repo_name))

    def form_activity_url(self):
        return ''.join((self.form_repo_url(), self.url_activity))

    @timeit
    def reserve_new_repo(self):
        success = False
        self.get_cursor().callproc('ReserveNextRepoForEvaluation', [self.machine_name])
        result = self.cursor.fetchone()
        if result is not None:
            self.repo_owner = result[0]
            self.repo_name = result[1]
            success = True
        return success

    @timeit
    def fetch_repo_info(self):
        self.fetch_repo_info_json = self.fetch_json_with_lock(self.form_repo_url())
        if self.fetch_repo_info_json is None:
            raise StopIteration('Restful Response did not form a parseable JSON document', self.form_repo_url())

        self.created_at, _ = iso_date_parser.parse(fetch_json_value('created_at', self.fetch_repo_info_json))
        self.updated_at, _ = iso_date_parser.parse(fetch_json_value('updated_at', self.fetch_repo_info_json))
        self.pushed_at, _ = iso_date_parser.parse(fetch_json_value('pushed_at', self.fetch_repo_info_json))
        self.homepage = fetch_json_value('homepage', self.fetch_repo_info_json)
        self.size = fetch_json_value('size', self.fetch_repo_info_json)
        self.watchers_count = fetch_json_value('watchers_count', self.fetch_repo_info_json)
        self.forks_count = fetch_json_value('forks_count', self.fetch_repo_info_json)
        self.network_count = fetch_json_value('network_count', self.fetch_repo_info_json)
        self.subscribers_count = fetch_json_value('subscribers_count', self.fetch_repo_info_json)

    @timeit
    def fetch_activity_info(self):
        self.fetch_activity_info_json = self.fetch_json_with_lock(self.form_activity_url())
        if self.fetch_activity_info_json is None:
            raise StopIteration('Restful Response did not form a parseable JSON document', self.form_activity_url())
        self.repo_last_year = Contributor('last_year_activity')
        for week in self.fetch_activity_info_json:
            total = fetch_json_value('total', week)
            ts = fetch_json_value('week', week)
            if total > 0:
                self.repo_last_year.add_week(ts, total)

    @staticmethod
    def sum(contrib_array):
        s = 0
        if contrib_array is not None and len(contrib_array) > 0:
            for c in contrib_array:
                if c is not None:
                    s += c.change_count if c.change_count is not None else 0
        return s

    @timeit
    def write_results_to_database(self):
        self.get_cursor()
        try:
            array = (self.repo_owner,
                     self.repo_name,
                     self.created_at,
                     self.updated_at,
                     self.pushed_at,
                     self.homepage,
                     self.size,
                     self.watchers_count,
                     self.sum([self.repo_last_year])
                     )
            self.get_cursor().callproc('EvaluateRepo', array)
        finally:
            self.close_cursor()

    @timeit
    def sleep_it_off(self):
        time.sleep(60)

    def main(self):
        MultiprocessMonitor(self.git_hub_lock, eval=self.get_stats)
        running = True
        while running:
            if self.reserve_new_repo():
                try:
                    self.fetch_repo_info()
                    try:
                        self.fetch_activity_info()
                    except StopIteration:
                        print('Unable to retrieve last years totals - continuing on')
                    self.write_results_to_database()
                except StopIteration as si:
                    print(si)
            else:
                self.sleep_it_off()


if __name__ == "__main__":
    _lock = Lock()
    subprocesses = [ChildProcessContainer(Investigator(_lock), 'inv')
                    ]
    for n in subprocesses:
        n.join()
else:
    print(__name__)
