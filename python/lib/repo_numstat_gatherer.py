import hashlib
import json
import os
import subprocess
import traceback
from datetime import datetime as datingdays
from shutil import disk_usage
from socket import gethostname
from threading import Lock, Event

import sys
import time

from child_process import ChildProcessContainer
from db_dependent_class import DBDependent, make_dir
from kitchen_sink_class import NumstatRequirementSet
from monitor import MultiprocessMonitor, timeit


class Author:
    def __init__(self, result_set):
        self.name_email = result_set['Author']
        self.md5 = None
        try:
            safe_auth = self.name_email.encode('utf-8')
            self.md5 = hashlib.md5(safe_auth).hexdigest()
        except Exception as e:
            b = bytearray(self.name_email, 'unicode-escape')
            self.md5 = hashlib.md5(b).hexdigest()
        if self.md5 is None:
            print('****************', self.name_email, 'produced NULL MD5SUM *************')
        self.min_date = datingdays.now().timestamp()
        self.max_date = 0
        self.commit_count = 0
        self.file_count = 0
        self.max_commits = 10
        self.last_ten = []
        self.first_commit = None
        self.last_commit = None
        self.add_result_set(result_set)

    def add_result_set(self, result_set):
        self.commit_count += 1
        commit_id = result_set['commit']
        date = datingdays.fromisoformat(result_set['Date']).timestamp()
        if date < self.min_date:
            self.min_date = date
            self.first_commit = commit_id
            self.last_ten.insert(0, {'dt': date, 'cid': commit_id, 'tz': result_set['orig_timezone']})
        if date > self.max_date:
            self.max_date = date
            self.last_commit = commit_id
            self.last_ten.insert(1, {'dt': date, 'cid': commit_id, 'tz': result_set['orig_timezone']})
        self.last_ten.insert(2, {'dt': date, 'cid': commit_id, 'tz': result_set['orig_timezone']})
        while len(self.last_ten) > self.max_commits:
            self.last_ten.pop()
        self.file_count += len(result_set['file_list'])


class RepoNumstatGatherer(DBDependent):
    def __init__(self, **kwargs):
        self.total_alias_processing_time = 0
        self.this_repo_commit_count = None
        DBDependent.__init__(self, **kwargs)
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
        self.MINIMUM_THRESHOLD = 1 * (1024 ** 3)
        self.repo_id = None
        self.url_prefix = 'https://github.com/'
        self.url_suffix = '.git'
        self.repo_dir = None
        self.results_file = None
        self.results_dir = None
        self.author_map = {}
        self.results_output_file = None
        self.success = None
        self.timeout_count = 0

    def stop(self):
        print('RepoNumstatGatherer is Leaving!')
        self.running = False
        self.interrupt_event.set()

    def get_total_alias_processing_time(self):
        return self.total_alias_processing_time;

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
        self.author_map = {}

        self.get_cursor()
        try:
            self.execute_procedure('ReserveRepoForNumstat', [self.machine_name])
            for goodness in self.get_cursor().stored_results():
                result = goodness.fetchone()
                if result:
                    self.repo_id = result[0]
                    self.owner = result[1]
                    self.repo_name = result[2]
                    self.repo_dir = result[3]
            if self.owner is not None and self.repo_name is not None:
                found_one = True
                self.current_repo = self.owner + '.' + self.repo_name
        finally:
            self.close_cursor()
        return found_one

    def build_batch_parameters(self, author, param_array):
        _last_ten = json.dumps(author.last_ten,
                               default=lambda o: o.__dict__,
                               sort_keys=True)
        _min = datingdays.fromtimestamp(author.min_date)
        _max = datingdays.fromtimestamp(author.max_date)
        param_array.append([author.md5,
                            author.name_email[0:(len(author.name_email) if len(author.name_email) < 256 else 255)],
                            author.commit_count,
                            _min,
                            _max,
                            self.owner,
                            self.repo_name,
                            _last_ten])

    @timeit
    def store_results_in_database(self):
        self.get_cursor()
        try:
            self.get_cursor()
            _min_date = datingdays.now().timestamp()
            _max_date = 0
            array_of_arrays = []
            param_array = []
            array_of_arrays.append(param_array)
            _start_time = time.time()
            _cnt = 0
            for v in self.author_map.values():
                self.build_batch_parameters(v, param_array)
                if v.min_date < _min_date:
                    _min_date = v.min_date
                if v.max_date > _max_date:
                    _max_date = v.max_date
                _cnt += 1
                if _cnt % 100 == 0:
                    param_array = []
                    array_of_arrays.append(param_array)

            self.total_alias_processing_time += (time.time() - _start_time)
            _start_time = time.time()
            for sub_array in array_of_arrays:
                self.cursor.executemany(
                    'insert into hacker_update_queue (md5, name_email, commit_count, min_date, max_date, repo_owner, repo_name, commit_array)' +
                    ' values (%s, %s, %s, %s, %s, %s, %s, %s);', sub_array)
            self.total_alias_processing_time += (time.time() - _start_time)

            self.execute_procedure('ReleaseRepoFromNumstat', [self.repo_id,
                                                              self.machine_name,
                                                              self.results_output_file,
                                                              datingdays.fromtimestamp(_min_date),
                                                              datingdays.fromtimestamp(_max_date),
                                                              self.this_repo_commit_count if self.this_repo_commit_count else 0,
                                                              self.success])
        finally:
            self.close_cursor()

    def commit_callback(self, commit):
        author = commit['Author']
        if author in self.author_map:
            self.author_map[author].add_result_set(commit)
        else:
            new_auth = Author(commit)
            self.author_map[author] = new_auth

    @timeit
    def report_timeout(self, proc):
        self.timeout_count += 1
        proc.kill()
        print("Timed out waiting for ", self.owner, "/", self.repo_name, " to execute numstat")

    @timeit
    def execute_numstats(self, cmd):
        numstat_req_set = NumstatRequirementSet()
        with subprocess.Popen(cmd, stdout=subprocess.PIPE) as proc:
            numstat_req_set.setup_background_process(proc.stdout, self.results_output_file, self.commit_callback)
            cpc = ChildProcessContainer(numstat_req_set, 'nmkid', numstat_req_set.why_cant_we_do_it_in_the_background)
            cpc.wait_for_it(900)
            if cpc.is_alive() and cpc.is_running() and not proc.poll():
                self.report_timeout(proc)
                return None
            return True

    @timeit
    def generate_numstats(self):
        rel_repo_path = './repos/' + self.owner + '/' + self.repo_name
        abs_repo_path = make_dir(rel_repo_path)
        rel_result_path = './results/' + self.owner + '/' + self.repo_name
        self.results_dir = make_dir(rel_result_path)
        self.results_file = self.results_dir + '/log_numstat.out'
        self.results_output_file = self.results_file + '.json.bz2'
        self.this_repo_commit_count = 0
        cmd = ['git', '-C', abs_repo_path, 'log', '--no-renames', '--numstat']
        # print(cmd)
        if self.git_lock:
            with self.git_lock:
                return self.execute_numstats(cmd)
        else:
            return self.execute_numstats(cmd)

    @timeit
    def release_job(self):
        self.execute_procedure('ReleaseRepoFromNumstat', (self.repo_id, self.machine_name, self.repo_dir))

    @timeit
    def idle_sleep(self):
        self.interrupt_event.wait(5)

    @timeit
    def error_sleep(self):
        self.interrupt_event.wait(60)

    @timeit
    def resource_sleep(self):
        self.interrupt_event.wait(60)

    @timeit
    def validate_repo_dir(self):
        return_val = False
        dir_name = './repos/'+self.owner+'/'+self.repo_name
        if os.path.isdir(dir_name) and os.path.exists(dir_name) and len(os.listdir(dir_name)) > 1:
            return_val = True
        return return_val

    @timeit
    def do_your_thing(self):
        self.monitor = MultiprocessMonitor(web_lock=self.web_lock, ds=self.get_disc_space, curjob=self.get_current_job,
                                           alias_tm=self.get_total_alias_processing_time)
        self.interrupt_event = Event()
        while self.running:
            if self.get_numeric_disc_space() >= self.MINIMUM_THRESHOLD:
                self.author_map = {}
                if self.reserve_next_repo():
                    self.success = False
                    try:
                        if self.validate_repo_dir() and self.generate_numstats():
                            self.success = True
                    except Exception as e:
                        print('Error encountered', e)
                        traceback.print_exc()
                        self.error_sleep()
                    finally:
                        self.store_results_in_database()
                else:
                    self.idle_sleep()
            else:
                self.resource_sleep()

    def main(self):
        self.do_your_thing()


if __name__ == "__main__":
    _lock = Lock()
    cpc = None
    try:
        rng = RepoNumstatGatherer(web_lock=_lock)
        cpc = ChildProcessContainer(rng, 'RepoNumstatGatherer')
    except Exception as e:
        print(e)
        traceback.print_exc()

    print(cpc)
    if cpc:
        cpc.join()
