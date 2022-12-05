from db_dependent_class import DBDependent
from git_hub_client import GitHubClient
import datetime as dt
import json
from threading import Lock


class RepoFinder(DBDependent, GitHubClient):
    def __init__(self, **kwargs):
        GitHubClient.__init__(self, **kwargs)
        DBDependent.__init__(self, **kwargs)
        self.repo_owner = None
        self.repo_name = None
        self.repo_id = None
        self.created_at = None
        self.updated_at = None
        self.pushed_at = None
        self.size = None
        self.watchers_count = None
        self.forks_count = None
        self.subscribers_count = None
        self.page_size = kwargs['page_size'] if 'page_size' in kwargs else 100
        self.min_size = kwargs['min_size'] if 'min_size' in kwargs else 100
        self.min_forks = kwargs['min_forks'] if 'min_forks' in kwargs else 1
        self.days_since_last_push = kwargs['days_since_last_push'] if 'days_since_last_push' in kwargs else 1
        self.language = kwargs['language'] if 'language' in kwargs else 'Java'
        self.url_prefix = 'https://api.github.com/search/repositories?'
        self.url_activity = 'page={}&per_page={}&q=size%3A>{}++forks%3A>{}+pushed%3A>{}+language%3A{}'
        self.page_num = 1

    def format_url(self):
        then = dt.datetime.now() - dt.timedelta(days=self.days_since_last_push)
        then_date = then.strftime('%Y-%m-%d')
        return ''.join((self.url_prefix, self.url_activity.format(self.page_num, self.page_size, self.min_size, self.min_forks, then_date, self.language)))

    def fetch_results(self):
        self.page_num = 1
        items_processed = 0
        items_expected = 1
        json_result = []
        done = False
        while items_processed < items_expected and not done:
            results = self.fetch_json_with_lock(self.format_url())
            if results is None:
                done = True
            else:
                items_expected = results['total_count']
                items = results['items']
                for i in items:
                    json_result.append(i)
                    items_processed += 1
                self.page_num += 1
                print('Processed ', items_processed, ' of ', items_expected)
        with open('results.json', 'w') as f:
            json.dump(json_result, f, indent=4)

    def main(self):
        self.fetch_results()


if __name__ == '__main__':
    rf = RepoFinder(web_lock=Lock())
    rf.main()

