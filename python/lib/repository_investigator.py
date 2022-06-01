import time
from db_dependent_class import DBDependent
from monitor import MultiprocessMonitor, timeit
from git_hub_client import GitHubClient
from git_hub_client import fetch_json_value
from datetime import datetime as datingdays
import iso_date_parser
from threading import Lock


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


class Investigator(DBDependent, GitHubClient):
    def __init__(self, lock):
        GitHubClient.__init__(self, lock)
        DBDependent.__init__(self)
        self.repo_last_year = None
        self.url_prefix = 'https://api.github.com/repos/'
        self.url_contributors = '/stats/contributors'
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
        self.contributors = None
        self.repo_contributor = None

    def form_repo_url(self):
        return ''.join((self.url_prefix, self.repo_owner, '/', self.repo_name))

    def form_contributors_url(self):
        return ''.join((self.form_repo_url(), self.url_contributors))

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
    def fetch_repo_info(self):  # Raises StopIteration Exception
        json = self.fetch_json_with_lock(self.form_repo_url())
        if json is None:
            raise StopIteration('Restful Response did not form a parseable JSON document', self.form_repo_url())

        self.created_at, _ = iso_date_parser.parse(fetch_json_value('created_at', json))
        self.updated_at, _ = iso_date_parser.parse(fetch_json_value('updated_at', json))
        self.pushed_at, _ = iso_date_parser.parse(fetch_json_value('pushed_at', json))
        self.homepage = fetch_json_value('homepage', json)
        self.size = fetch_json_value('size', json)
        self.watchers_count = fetch_json_value('watchers_count', json)
        self.forks_count = fetch_json_value('forks_count', json)
        self.network_count = fetch_json_value('network_count', json)
        self.subscribers_count = fetch_json_value('subscribers_count', json)

    @timeit
    def fetch_contributor_info(self):
        json = self.fetch_json_with_lock(self.form_contributors_url())
        if json is None:
            raise StopIteration('Restful Response did not form a parseable JSON document', self.form_contributors_url())
        self.contributors = []
        self.repo_contributor = Contributor('contributor_counts')
        for contributor in json:
            # JSON doc is an array of "contributor" objects
            total = fetch_json_value('total', contributor)
            author = fetch_json_value('author.login', contributor)
            c = Contributor(author)
            self.contributors.append(c)
            weeks = fetch_json_value('weeks', contributor)
            for w in weeks:
                ts = fetch_json_value('w', w)
                added = fetch_json_value('a', w)
                deleted = fetch_json_value('d', w)
                changed = fetch_json_value('c', w)
                ttl = added+deleted+changed;
                if ttl > 0:
                    c.add_week(ts, ttl)
                    self.repo_contributor.add_week(ts, ttl)

    @timeit
    def fetch_activity_info(self):
        json = self.fetch_json_with_lock(self.form_activity_url())
        if json is None:
            raise StopIteration('Restful Response did not form a parseable JSON document', self.form_contributors_url())
        self.repo_last_year = Contributor('last_year_activity')
        for week in json:
            total = fetch_json_value('total', week)
            ts = fetch_json_value('week', week)
            if total > 0:
                self.repo_last_year.add_week(ts, total)

    @staticmethod
    def sum(contrib_array):
        s = 0
        for c in contrib_array:
            s += c.change_count
        return s

    @timeit
    def write_results_to_database(self):
        array = (self.repo_owner,
                 self.repo_name,
                 self.created_at,
                 self.updated_at,
                 self.pushed_at,
                 self.homepage,
                 self.size,
                 self.watchers_count,
                 len(self.contributors),
                 self.sum(self.contributors),
                 self.sum([self.repo_last_year])
                 )
        self.get_cursor().callproc('EvaluateRepo', array)

    @timeit
    def sleep_it_off(self):
        time.sleep(60)

    def my_tracer(self, frame, event, arg = None):
        # extracts frame code
        code = frame.f_code

        # extracts calling function name
        func_name = code.co_name

        # extracts the line number
        line_no = frame.f_lineno
        msg = datingdays.now().strftime('%a %b %d %H:%M:%S.%f')[:-4]+':'

        print(msg, f"A {event} encountered in \
        {func_name}() at line number {line_no} ")

        return self.my_tracer

    def main(self):
        MultiprocessMonitor(
            self.git_hub_lock,
            eval=self.get_stats)
        running = True
        while running:
            if self.reserve_new_repo():
                try:
                    self.fetch_repo_info()
                    self.fetch_contributor_info()
                    self.fetch_activity_info()
                    self.write_results_to_database()
                except StopIteration as si:
                    print(si)
            else:
                self.sleep_it_off()


if __name__ == "__main__":
    Investigator(Lock()).main()
else:
    print(__name__)

