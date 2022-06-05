import json
import mysql.connector
import os


def make_dir(dir_name):
    if not os.path.isdir(dir_name) and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return os.path.abspath(dir_name)


class DBDependent:
    def __init__(self):
        self.db_config = None
        self.database = None
        self.cursor = None

    def load_db_info(self):
        if self.db_config is None:
            with open('./db.cfg', 'r') as r:
                self.db_config = json.load(r)

    def close_cursor(self):
        self.cursor.close()
        self.cursor = None
        self.database.close()
        self.database = None

    def get_cursor(self):
        if self.database is None:
            self.load_db_info()
            self.database = mysql.connector.connect(
                port=self.db_config['port'],
                host=self.db_config['host'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database'],
                autocommit=bool(self.db_config['autocommit']))
        if self.cursor is None:
            self.cursor = self.database.cursor()
        return self.cursor
