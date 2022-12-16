import json
import os
from socket import gethostname

import mysql.connector
import psutil
import sys

from lib.monitor import timeit
from lib.signal_handler import SignalHandler


def make_dir(dir_name):
    if not os.path.isdir(dir_name) and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return os.path.abspath(dir_name)


def mem_info():
    return psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2


class DBDependent(SignalHandler):

    def __init__(self, **kwargs):
        SignalHandler().__init__()
        self.db_config = None
        self.database = None
        self.cursor = None
        self.stack = None
        self.machine_name = os.uname().nodename if sys.platform != "win32" else gethostname()
        self.db_lock = kwargs['database_lock'] if 'database_lock' in kwargs else None
        self.web_lock = kwargs['web_lock'] if 'web_lock' in kwargs else None
        self.git_lock = kwargs['git_lock'] if 'git_lock' in kwargs else None

    @timeit
    def kill_all_subprocesses(self, proc):
        pid = proc.pid if proc.pid else os.getpid()
        me = psutil.Process(pid)
        for child in me.children(recursive=True):
            print(f'Killing child process {child.pid}: {child.cmdline()}')
            child.kill()

    @timeit
    def execute_procedure(self, method_name, params):
        if self.db_lock:
            with self.db_lock:
                return self.get_cursor().callproc(method_name, params)
        else:
            return self.get_cursor().callproc(method_name, params)

    @timeit
    def delay_repo_processing(self, _in_repo_id):
        self.execute_procedure('DelayAPICallsForRepo', [_in_repo_id])

    def load_db_info(self):
        if self.db_config is None:
            with open('./db.cfg', 'r') as r:
                self.db_config = json.load(r)

    def close_cursor(self):
        if self.cursor:
            self.cursor.close()
        self.cursor = None
        if self.database:
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
