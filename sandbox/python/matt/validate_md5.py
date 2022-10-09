import sys
local_lib_dir = '../python/lib/'
sys.path.append(local_lib_dir)
from db_dependent_class import DBDependent
import hashlib


def synthetic_partition_key(owner, repo_name):
    partition_key = owner + "\t" + repo_name
    return hashlib.md5(partition_key.encode('utf-8')).hexdigest()

class ValidateMD5(DBDependent):
    def __init__(self):
        DBDependent.__init__(self)
        self.load_db_info()

    def run(self):
        self.get_cursor().execute('SELECT id, owner, name, md5 FROM `repo`')
        cnt = 0
        for row in self.cursor:
            repo_id = row[0]
            owner = row[1]
            name = row[2]
            md5 = row[3]
            if md5 is None:
                continue
            if md5 != synthetic_partition_key(owner, name):
                print(f'Bad md5 for repo {repo_id} {owner}/{name} {md5} != {synthetic_partition_key(owner, name)}')
            cnt += 1
            if cnt % 1000 == 0:
                print(f'{cnt} repos checked')


if __name__ == '__main__':
    ValidateMD5().run()