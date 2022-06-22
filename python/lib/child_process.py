import threading
from threading import Thread

import time

from monitor import timeit


class ChildProcessContainer(Thread):

    def __init__(self, managed_instance, proc_name, run_method=None):
        self.thread = None
        super().__init__(target=self.run, daemon=False, name=proc_name)
        self.managed_instance = managed_instance
        self.run_method = run_method if run_method else managed_instance.main
        self.running = True
        self.start()

    @timeit
    def wait_for_it_to_start(self, seconds):
        start_time = time.time()
        while not self.thread and (time.time() - start_time) < seconds:
            time.sleep(0.2)

    def wait_for_it(self, seconds):
        init_time = time.time()
        self.wait_for_it_to_start(seconds)
        if not self.thread:
            raise StopIteration('ChildProcessContainer timed out waiting for thread to go "live"')

        self.thread.join(seconds-(time.time()-init_time))

    def stop(self):
        stop_method = getattr(self.managed_instance, 'stop', default=-1)
        if stop_method and callable(stop_method):
            stop_method(self.managed_instance)

    def is_running(self):
        return self.running

    def run(self):
        try:
            self.thread = threading.current_thread()
            self.run_method()
        finally:
            self.running = False
