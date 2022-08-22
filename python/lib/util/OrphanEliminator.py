import sys
from os.path import exists

sys.path.append("../../python/lib")
from db_dependent_class import DBDependent


class OrphanEliminator(DBDependent):
    def __init__(self):
        DBDependent.__init__(self)
        self.find_orphan_sql = """
            select c.id from commit c
            left join repo_commit rc on rc.commit_id = c.id 
            where rc.id is NULL;
        """
        self.delete_sql = """
            delete from commit where id = %s;
        """
        self.database = None

    def main(self):
        id_array = []
        c = self.get_cursor()
        if exists('orphan_commits.txt'):
            with open('orphan_commits.txt', 'rt') as r:
                for line in r:
                    id_array.append(line.strip())
        else:
            with open('orphan_commits.txt', 'wt') as w:
                c.execute(self.find_orphan_sql)
                for row in c.fetchall():
                    id_array.append(row[0])
                    w.write('' + str(row[0]) + '\n')
        print('Done loading orphans')
        batch = []
        cnt = 0
        for id in id_array:
            batch.append([id])
            cnt += 1
            if cnt % 100 == 0:
                c.executemany(self.delete_sql, batch)
                batch = []
                print(cnt, 'commits deleted')
        if len(batch) > 0:
            c.executemany(self.delete_sql, batch)
            cnt += len(batch)
            batch = []
        print(f'{cnt} rows deleted')


if __name__ == '__main__':
    OrphanEliminator().main()