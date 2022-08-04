import base64
import bz2
import hashlib
import json
from datetime import datetime as datingdays

import time

from db_dependent_class import mem_info
from monitor import Monitor, timeit
from repo_numstat_gatherer import RepoNumstatGatherer


class Alias:
    def __init__(self, commit):
        self.alias = commit['Author']
        self.md5 = hashlib.md5(self.alias).hexdigest()
        self.min_date = datingdays.now().timestamp()
        self.max_date = 0
        self.commit_count = 0
        self.update(commit)

    def update(self, commit):
        date = datingdays.fromisoformat(commit['Date'])
        if date.timestamp() < self.min_date:
            self.min_date = date.timestamp()
        if date.timestamp() > self.max_date:
            self.max_date = date.timestamp()
        self.commit_count += 1


class RecoverAliases(RepoNumstatGatherer):
    def __init__(self, **kwargs):
        RepoNumstatGatherer.__init__(self, **kwargs)
        self.running = True
        self.monitor = Monitor(frequency=5,mem=mem_info,bytes_rcvd=self.get_bytes_rcvd)
        self.fetch_contributor_info_json = None
        self.alias_map = {}
        self.bytes_rcvd = 0
        self.last_id = 0

    def get_bytes_rcvd(self):
        return f'{self.bytes_rcvd/(1.0*1024**2): 0.3f}mb'

    @timeit
    def touche(self):
        pass

    @timeit
    def error_sleep(self, e):
        print(f'Error processing numstat {self.last_id}: {e}')
        time.sleep(2)


    @timeit
    def process_numstat(self, str):
        if str and len(str) > 0:
            self.bytes_rcvd += len(str)
            try:
                binary = base64.b64decode(str)
                raw_numstat = bz2.decompress(binary)
                numstat = json.loads(raw_numstat)
                for commit in numstat:
                    self.commit_callback(commit)
            except Exception as e:
                self.error_sleep(e)

    def run(self):
        self.touche()
        running = True
        while running:
            print(f'String next query at {self.last_id}')
            self.get_cursor().execute(f'select numstat, id From repo_numstat where numstat is not null and id > {self.last_id} order by id limit 1000')
            cnt = 0
            for row in self.cursor:
                self.last_id = row[1]
                self.process_numstat(row[0])
                cnt += 1
            if cnt == 0:
                running = False
            else:
                self.close_cursor()
                self.store_results_in_database()
                self.alias_map = {}



if __name__ == '__main__':
    RecoverAliases().run()
