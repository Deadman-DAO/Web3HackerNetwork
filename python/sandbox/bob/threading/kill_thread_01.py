from time import sleep, perf_counter
import threading
import ctypes
import time

class ThreadWithException(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        
    def run(self):
        try:
            while True:
                print('running ' + self.name)
                sleep(1)
        finally:
            print('ended')

    def get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        print('entering raise_exception')
        thread_id = self.get_id()
        print(f'thread ID is {thread_id}')
        c_thread_id = ctypes.c_long(thread_id)
        print(f'c_thread_ID is {c_thread_id}')
        sysexit_obj = ctypes.py_object(SystemExit)
        print(f'sysexit_obj is {sysexit_obj}')
        res = ctypes.pythonapi. \
            PyThreadState_SetAsyncExc( c_thread_id, sysexit_obj )
        print(f'res is {res}')
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

t1 = ThreadWithException('Thread 1')
t1.start()
time.sleep(2)
print('calling raise_exception')
t1.raise_exception()
print('raise_exception has returned')
print('calling join')
t1.join()
print('join has joined')

