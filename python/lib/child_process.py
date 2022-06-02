import sys
from threading import Thread
import traceback


class ChildProcessContainer(Thread):

    def __init__(self, managed_instance, proc_name):
        super().__init__(target=self.run, daemon=False, name=proc_name)
        self.managed_instance = managed_instance
        self.start()

    def run(self):
        self.managed_instance.main()
