from lib.db_dependent_class import DBDependent
import os
import json
import bz2
import sys

class Flattener(DBDependent):
    def __init__(self, repo_owner, repo_name):
        DBDependent.__init__(self)
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.numstat_dir = os.path.join('./results/', self.repo_owner, self.repo_name)
        self.numstat_path = os.path.join(self.numstat_dir, 'log_numstat.out.json.bz2')
        self.numstat_raw = None
        self.numstat_json = None
        self.numstat = None
        self.flat = []
        self.json_flat = None
        self.flat_stack = []

    def main(self):
        with open(self.numstat_path, 'rb') as r:
            self.numstat_raw = r.read()
        self.numstat_json = bz2.decompress(self.numstat_raw)
        self.numstat = json.loads(self.numstat_json)
        idx = 0
        for commit in self.numstat:
            idx += 1
            self.flat.append((commit['commit'], self.machine_name))
            if idx % 100 == 0:
                self.flat_stack.append(self.flat)
                self.flat = []
        for elem in self.flat_stack:
            self.get_cursor().executemany('insert into commit_check (commit_hash, machine_name) values (%s, %s)', elem)

        self.json_flat = json.dumps(self.flat, indent=4)
        with open(os.path.join(self.numstat_dir, 'flat.json'), 'w') as w:
            w.write(self.json_flat)
        self.execute_procedure('FindNewCommitIDs', (self.json_flat, self.machine_name)))
        for goodness in self.get_cursor().stored_results():
            result = goodness.fetchone()
            if result is not None:
                print(result[0])
        print('Done!')

if __name__ == '__main__':
    owner = 'master-hzz'
    name = 'tensorflow'
    if len(sys.argv) > 2:
        owner = sys.argv[1]
        name = sys.argv[2]
    Flattener(owner, name).main()
