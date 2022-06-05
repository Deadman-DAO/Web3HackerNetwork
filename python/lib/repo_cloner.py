from db_dependent_class import DBDependent, make_dir
from monitor import MultiprocessMonitor, timeit
import os
import sys
from socket import gethostname
import threading
from shutil import disk_usage
from threading import Lock


class RepoCloner(DBDependent):
    def __init__(self, lock):
        self.lock = lock
        DBDependent.__init__(self)
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
        self.MINIMUM_THRESHOLD = 5 * (1024 ** 3)
        self.repo_id = None
        self.url_prefix = 'https://github.com/'
        self.url_suffix = '.git'
        self.repo_dir = None

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
        self.cursor.callproc('ReserveNextRepo', (self.machine_name, None, None, None))
        if self.cursor.sp_outparams:  # one or more inline results set ready
            result = self.cursor.fetchone()
            self.owner = result[0]
            self.repo_name = result[1]
            self.repo_id = result[2]
        if self.owner is not None and self.repo_name is not None:
            found_one = True
            self.current_repo = self.owner + '.' + self.repo_name
        return found_one

    @timeit
    def clone_it(self):
        self.repo_dir = make_dir('./repos/' + self.owner + '/' + self.repo_name)
        cmd = str('git -C ./repos/' + self.owner + '/ clone ' + self.format_url() + (' 2> /dev/null' if sys.platform != "win32" else ''))
        print(cmd)
        return_value = os.system(cmd)
        if return_value != 0:
            raise StopIteration('Error encountered - git clone exited with a value of ' + str(return_value))

    @timeit
    def release_job(self):
        self.get_cursor().callproc('ReleaseRepoFromCloning', (self.repo_id, self.machine_name, self.repo_dir))

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
        self.monitor = MultiprocessMonitor(self.lock, ds=self.get_disc_space, curjob=self.get_current_job)
        self.interrupt_event = threading.Event()
        while self.running:
            if self.get_numeric_disc_space() >= self.MINIMUM_THRESHOLD:
                if self.reserve_next_repo():
                    try:
                        self.clone_it()
                    except Exception as e:
                        print('Error encountered', e)
                        self.error_sleep()
                    finally:
                        self.release_job()
                else:
                    self.idle_sleep()
            else:
                self.resource_sleep()


if __name__ == "__main__":
    RepoCloner(Lock()).main()
