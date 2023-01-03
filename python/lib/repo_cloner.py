import os
import threading
import traceback
from shutil import disk_usage
from socket import gethostname
from subprocess import TimeoutExpired, Popen
from threading import Lock

import requests
import sys
import time

from lib.child_process import ChildProcessContainer
from lib.db_dependent_class import DBDependent, make_dir
from lib.monitor import MultiprocessMonitor, timeit, find_argv_param
from sandbox.matt.log_trial import clog as log


class RepoCloner(DBDependent):
    def __init__(self, **kwargs):
        DBDependent.__init__(self, **kwargs)
        self.timeout_counter = 0
        self.success = None
        self.monitor = None
        self.repo_base_dir = './repos'
        make_dir(self.repo_base_dir)
        self.machine_name = os.uname().nodename if sys.platform != "win32" else gethostname()
        self.database = None
        self.db_config = None
        self.current_repo = None
        self.owner = None
        self.repo_name = None
        self.running = True
        self.thread = None
        self.interrupt_event = threading.Event()
        self.MINIMUM_THRESHOLD = 7 * (1024 ** 3)
        self.RESTING_THRESHOLD = 9 * (1024 ** 3)
        self.resting = False
        self.repo_id = None
        self.url_prefix = 'https://github.com/'
        self.url_suffix = '.git'
        self.repo_dir = None
        self.clone_started = None
        self.lock_acquired = None
        self.max_wait = self.get_env_var('MAX_GIT_WAIT_SECONDS', default_val='360', wrapper_method=int)
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
    def report_timeout(self, proc):
        self.timeout_counter += 1
        expired = time.time() - self.clone_started
        lock_time = time.time() - self.lock_acquired
        self.kill_all_subprocesses(proc)
        proc.kill()
        print('Terminating long running thread for ', self.owner, self.repo_name, expired,
              'seconds since start time.', lock_time, 'seconds since lock acquired.')

    @timeit
    def got_lock_now_cloning(self, cmd) -> (bool, str, str) :
        self.lock_acquired = time.time()
        return self.execute_os_cmd(cmd, max_wait=self.max_wait, report_timeout_proc=self.report_timeout)

    @timeit
    def clone_it(self) -> (bool, str, str):
        self.repo_dir = make_dir('./repos/' + self.owner + '/' + self.repo_name)
        url = 'https://github.com/'+self.owner+'/'+self.repo_name+'.git'
        html_reply = requests.get(url, headers=self.headers)
        if html_reply.status_code != 200:
            with open('./clone_it.err', 'wb') as wb:
                wb.write(html_reply.content)
            raise StopIteration('Reply code {rc} returned from {url} - pausing and skipping'.
                                format(rc=html_reply.status_code, url=url))
        cmd = ['nice',  'git', '-C', './repos/' + self.owner + '/', 'clone', self.format_url()]
        if sys.platform == "win32":
            # Take out the first element of the cmd array as windows isn't "nice"
            cmd = cmd[1:]
        # print(cmd)
        self.clone_started = time.time()
        if self.git_lock:
            with self.git_lock:
                return self.got_lock_now_cloning(cmd)
        else:
            return self.got_lock_now_cloning(cmd)

    @timeit
    def release_job(self):
        log.info(f'Releasing job {self.current_repo} with success {self.success}')
        self.execute_procedure('ReleaseRepoFromCloning', (self.repo_id, self.machine_name, self.repo_dir, self.success))

    @timeit
    def idle_sleep(self):
        self.interrupt_event.wait(5)

    @timeit
    def error_sleep(self):
        self.close_cursor()
        self.interrupt_event.wait(60)

    @timeit
    def resource_sleep(self):
        self.interrupt_event.wait(60)

    def main(self):
        self.monitor = MultiprocessMonitor(web_lock=self.web_lock, ds=self.get_disc_space, curjob=self.get_current_job)
        while self.running:
            try:
                if self.get_numeric_disc_space() >= (self.RESTING_THRESHOLD if self.resting else self.MINIMUM_THRESHOLD):
                    self.resting = False
                    if self.reserve_next_repo():
                        self.success = False
                        try:
                            self.success, _, _ = self.clone_it()
                        except Exception as e:
                            print('Error encountered', e)
                            traceback.print_exc()
                            self.error_sleep()
                        finally:
                            self.release_job()
                            if not self.success:
                                self.error_sleep()
                    else:
                        self.idle_sleep()
                else:
                    self.current_repo = 'waiting_for_disc_space'
                    self.resting = True
                    self.resource_sleep()
            except Exception as anything:
                print(anything)
                traceback.print_exc()
                self.error_sleep()


if __name__ == "__main__":
    if len(sys.argv) > 2:
        owner = sys.argv[1]
        repo_name = sys.argv[2]
        rc = RepoCloner(web_lock=Lock(), git_lock=Lock())
        rc.owner = owner
        rc.repo_name = repo_name
        a, b, c = rc.clone_it()
        print(a, b, c)
    else:
        RepoCloner(web_lock=Lock(), git_lock=Lock()).main()
