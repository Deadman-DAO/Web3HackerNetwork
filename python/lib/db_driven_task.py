from abc import ABC, abstractmethod
from db_dependent_class import DBDependent
from monitor import MultiprocessMonitor, timeit
import sys
import os
from socket import gethostname
from threading import Lock
import traceback
import threading


class DBTask(ABC):
    @abstractmethod
    def get_proc_name(self):
        """ return SQL procedure name string """
        pass

    @abstractmethod
    def get_proc_parameters(self):
        """ return array of procedural parameters """
        pass

    @abstractmethod
    def process_db_results(self, result_args):
        """ given the db.callproc() return value go do your thing
            ***return back*** any object for success, None for no further processing necessary,
            and raise Exception if trouble encountered
        """
        pass


class DBDrivenTaskProcessor(ABC, DBDependent):
    def __init__(self, **kwargs):
        DBDependent.__init__(self, **kwargs)
        self.monitor = None
        self.running = True
        self.idle_wait = int(kwargs['idle_wait']) if 'idle_wait' in kwargs else 5
        self.error_wait = int(kwargs['error_wait']) if 'error_wait' in kwargs else 60
        self.machine_name = os.uname().nodename if sys.platform != "win32" else gethostname()
        self.interrupt_event = None

    @abstractmethod
    def get_job_fetching_task(self):
        """ Return an instance of DBTask for retrieving the next job for this class to work on """
        pass

    @abstractmethod
    def get_job_completion_task(self):
        """ Return an instance of DBTask for reporting job completion """
        pass

    def call_db_proc(self, db_task):
        result = None
        try:
            result = db_task.process_db_results(
                self.execute_procedure(db_task.get_proc_name(), db_task.get_proc_parameters()))
        finally:
            self.close_cursor()
        return result

    @timeit
    def fetch_next_task(self):
        return self.call_db_proc(self.get_job_fetching_task())

    @timeit
    def complete_task(self):
        proc = self.get_job_completion_task()
        if proc:
            return self.call_db_proc(proc)
        else:
            return None

    @abstractmethod
    def process_task(self):
        """
        Based on a non-None return value from job_fetching_task.process_db_results
        implement this method to complete any processing necessary
        :return:
        no return value necessary - raise Exception if bad things happen
        """
        pass

    @timeit
    def idle_sleep(self):
        self.interrupt_event.wait(self.idle_wait)

    @timeit
    def error_sleep(self):
        self.interrupt_event.wait(self.error_wait)

    @abstractmethod
    def init(self):
        """
        get done here things like self.monitor.add_display_methods
        """
        pass

    def main(self):
        self.interrupt_event = threading.Event()
        print('Entering MAIN')
        self.monitor = MultiprocessMonitor(web_lock=self.web_lock)
        self.init()
        while self.running:
            try:
                task = self.fetch_next_task()
                if task:
                    try:
                        self.process_task()
                    finally:
                        self.complete_task()
                else:
                    self.idle_sleep()
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                self.error_sleep()

    def stop(self):
        self.running = False
        self.interrupt_event.set()
