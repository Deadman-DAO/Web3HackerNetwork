import base64
import os

from db_dependent_class import DBDependent


class FindersCleaners(DBDependent):
    def __init__(self):
        DBDependent.__init__(self)

    def process(self, path):
        if os.path.isdir(path):
            for n in os.listdir(path):
                self.process(os.path.join(path, n))
        elif path.endswith(".json.bz2"):
            repo_name = os.path.dirname(path)
            owner = os.path.dirname(repo_name)
            repo_name = os.path.basename(repo_name)
            owner = os.path.basename(owner)
            with open(path, 'rb') as r:
                numstat = r.read()
            numstat = base64.b64encode(numstat)

            self.get_cursor().execute('''
                  insert into repo_numstat (repo_id, tstamp, numstat)
                  select r.id, current_timestamp(3), %s from repo r left join repo_numstat rn on rn.repo_id = r.id 
                  where rn.id is null and name = %s and owner = %s;
                  ''',
                [numstat, repo_name, owner])
            print('Completed ', os.path.abspath(path))

    def main(self):
        self.process("./results")


if __name__ == '__main__':
    FindersCleaners().main()