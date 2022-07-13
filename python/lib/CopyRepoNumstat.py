import json

import mysql.connector

from db_dependent_class import DBDependent


class CopyRepoNumstat(DBDependent):

    def __init__(self, **kwargs):
        DBDependent.__init__(self, **kwargs)
        with open('./target_db.cfg', 'r') as r:
            self.from_db_config = json.load(r)
        self.select_sql = 'select repo_id, tstamp, numstat, numstat_size from repo_numstat;'
        self.insert_sql = 'insert into repo_numstat (repo_id, tstamp, numstat, numstat_size) values (%s, %s, %s, %s) on duplicate key update tstamp = now(3);'
        self.from_dbase = None
        self.from_cursor = None

    def run(self):
        self.from_dbase = mysql.connector.connect(
            port=self.from_db_config['port'],
            host=self.from_db_config['host'],
            user=self.from_db_config['user'],
            password=self.from_db_config['password'],
            database=self.from_db_config['database'],
            autocommit=bool(self.from_db_config['autocommit']))
        self.from_cursor = self.from_dbase.cursor()

        self.from_cursor.execute(self.select_sql)
        count = 0
        block_size = 100
        array = []
        for row in self.from_cursor:
            array.append(row)
            if len(array) >= block_size:
                self.get_cursor().executemany(self.insert_sql, array)
                array = []

            count += 1
            if count % block_size == 0:
                print(count, 'records copied')
        print('FINAL: ', count, 'records copied')


if __name__ == "__main__":
    CopyRepoNumstat().run()