import json
import mariadb


class DBDependent:
    def __init__(self):
        self.db_config = None
        self.database = None
        self.cursor = None

    def load_db_info(self):
        if self.db_config is None:
            with open('./db.cfg', 'r') as r:
                self.db_config = json.load(r)

    def get_cursor(self):
        if self.database is None:
            self.load_db_info()
            self.database = mariadb.connect(
                port=self.db_config['port'],
                host=self.db_config['host'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database'],
                autocommit=(self.db_config['autocommit'] == 'true'))
            self.cursor = self.database.cursor()
        return self.cursor
