import os
import threading
from shutil import disk_usage
from socket import gethostname
from subprocess import TimeoutExpired, run
from threading import Lock

import requests
import sys

from child_process import ChildProcessContainer
from db_dependent_class import DBDependent, make_dir
from monitor import MultiprocessMonitor, timeit


class RepoCloner(DBDependent):
    def __init__(self, **kwargs):
        DBDependent.__init__(self, **kwargs)
        self.timeout_counter = None
        self.success = None
        self.monitor = None
        self.repo_base_dir = './repos'
        make_dir(self.repo_base_dir)
        self.machine_name = os.uname().nodename if sys.platform != "win32" else gethostname()
        self.database = None
        self.db_config = None
        self.current_repo = ''
        self.owner = None
        self.repo_name = None
        self.running = True
        self.thread = None
        self.interrupt_event = None
        self.MINIMUM_THRESHOLD = 10 * (1024 ** 3)
        self.RESTING_THRESHOLD = 15 * (1024 ** 3)
        self.resting = False
        self.repo_id = None
        self.url_prefix = 'https://github.com/'
        self.url_suffix = '.git'
        self.repo_dir = None
        with open('./web3.github.token', 'r') as f:
            self.token = f.readline()
            self.token = self.token.strip('\n')
            self.headers = {'Authorization': 'token %s' % self.token}

    def stop(self):
        self.running = False
        self.interrupt_event.set()

    def format_url(self):
        return self.url_prefix + self.owner + '/' + self.repo_name + self.url_suffix

    def get_numeric_disc_space(self):
        return disk_usage(self.repo_base_dir).free

    def get_disc_space(self):
        return f'{(self.get_numeric_disc_space() / (1024 ** 3)):0.3f}'

    def get_current_job(self):
        return self.current_repo if self.current_repo is not None else '<IDLE>'

    @timeit
    def reserve_next_repo(self):
        found_one = False
        self.owner = None
        self.repo_name = None

        self.get_cursor()
        try:
            result = self.execute_procedure('ReserveNextRepo', (self.machine_name, None, None, None))
            if result:
                self.owner = result[1]
                self.repo_name = result[2]
                self.repo_id = result[3]
                if self.owner is not None and self.repo_name is not None:
                    found_one = True
                    self.current_repo = self.owner + '.' + self.repo_name
        finally:
            self.close_cursor()
        return found_one

    @timeit
    def report_timeout(self):
        self.timeout_counter += 1
        print('Terminating long running thread for ', self.owner, self.repo_name)

    @timeit
    def clone_it(self):
        self.repo_dir = make_dir('./repos/' + self.owner + '/' + self.repo_name)
        url = 'https://github.com/'+self.owner+'/'+self.repo_name+'.git'
        html_reply = requests.get(url, headers=self.headers)
        if html_reply.status_code != 200:
            with open('./clone_it.err', 'wb') as wb:
                wb.write(html_reply.content)
            raise StopIteration('Reply code {rc} returned from {url} - pausing and skipping'.format(rc=html_reply.status_code, url=url))
        cmd = ['git', '-C', './repos/' + self.owner + '/', 'clone', self.format_url()]
        # print(cmd)
        try:
            run(cmd, timeout=900)
        except TimeoutExpired:
            self.report_timeout()

    @timeit
    def release_job(self):
        self.execute_procedure('ReleaseRepoFromCloning', (self.repo_id, self.machine_name, self.repo_dir, self.success))

    @timeit
    def idle_sleep(self):
        self.interrupt_event.wait(5)

    @timeit
    def error_sleep(self):
        self.interrupt_event.wait(60)

    @timeit
    def resource_sleep(self):
        self.interrupt_event.wait(60)

    def main(self):
        self.monitor = MultiprocessMonitor(web_lock=self.web_lock, ds=self.get_disc_space, curjob=self.get_current_job)
        self.interrupt_event = threading.Event()
        while self.running:
            if self.get_numeric_disc_space() >= self.RESTING_THRESHOLD if self.resting else self.MINIMUM_THRESHOLD:
                self.resting = False
                if self.reserve_next_repo():
                    self.success = False
                    try:
                        self.clone_it()
                        self.success = True
                    except Exception as e:
                        print('Error encountered', e)
                        self.error_sleep()
                    finally:
                        self.release_job()
                else:
                    self.idle_sleep()
            else:
                self.resting = True
                self.resource_sleep()


if __name__ == "__main__":
    _lock = Lock()
    subprocesses = [ChildProcessContainer(RepoCloner(web_lock=Lock()), 'RepoCloner')
                    ]
    for n in subprocesses:
        n.join()
