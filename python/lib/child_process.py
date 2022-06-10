import threading
from threading import Thread


class ChildProcessContainer(Thread):

    def __init__(self, managed_instance, proc_name):
        self.thread = None
        super().__init__(target=self.run, daemon=False, name=proc_name)
        self.managed_instance = managed_instance
        self.start()

    def stop(self):
        stop_method = getattr(self.managed_instance, 'stop')
        if stop_method and callable(stop_method):
            stop_method(self.managed_instance)

    def run(self):
        self.thread = threading.current_thread()
        self.managed_instance.main()
