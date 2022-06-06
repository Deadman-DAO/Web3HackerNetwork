import os

import time
import psutil
from datetime import datetime as datingdays
from functools import wraps
from threading import Thread, current_thread, Lock


def concat(*args):
    ret_val = ''
    for n in args:
        ret_val = ret_val + (n if isinstance(n, str) else str(n))
    return ret_val


class Tracker:
    def __init__(self):
        self.call_count = 0
        self.exec_time = 0

    def __str__(self):
        return concat('call_count:',self.call_count,' exec_time:', self.exec_time)


class MonitoredThread(object):
    def __init__(self):
        self.monitor_timer_map = {}
        self.monitor_current_method = ''
        self.monitor_call_stack = []
        self.start_time = 0
        self.result = None
        self.end_time = 0
        self.tracker = None


monitored_thread_map = {}
monitor_lock = None


def mem_info():
    return str(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)


def get_monitored_thread(thread_name=None):
    global monitored_thread_map
    _ct_name = current_thread().name if thread_name is None else thread_name
    if _ct_name not in monitored_thread_map:
        monitored_thread_map[_ct_name] = MonitoredThread()
    return monitored_thread_map[_ct_name]


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        global monitored_thread_map
        global monitor_lock
        mt = get_monitored_thread()
        mt.monitor_current_method = func.__name__
        mt.monitor_call_stack.insert(0, mt.monitor_current_method)
        mt.start_time = datingdays.now().timestamp()
        try:
            mt.result = func(*args, **kwargs)
        finally:
            mt.end_time = datingdays.now().timestamp()
            mt.total_time = mt.end_time - mt.start_time
            mt.tracker = mt.monitor_timer_map[func.__name__] if func.__name__ in mt.monitor_timer_map else None
            if mt.tracker is None:
                mt.tracker = Tracker()
                with monitor_lock:
                    mt.monitor_timer_map[func.__name__] = mt.tracker
            mt.tracker.call_count += 1
            mt.tracker.exec_time += mt.total_time
            mt.monitor_call_stack.remove(mt.monitor_call_stack[0])
            mt.monitor_current_method = mt.monitor_call_stack[0] if len(mt.monitor_call_stack) > 0 else 'Unknown!'
        return mt.result
    return timeit_wrapper


class Monitor:
    def __init__(self, **kwargs):
        global monitor_lock
        if monitor_lock is None:
            monitor_lock = Lock()
        self.my_lock = monitor_lock
        self.process_map = {}
        self.add_thread(**kwargs)
        self.process = Thread(target=self.run, daemon=True, name='Monitor')
        self.process.start()
        self.start_time = datingdays.now().timestamp()

    def add_thread(self, **kwargs):
        ct_name = current_thread().name
        self.process_map[ct_name] = kwargs
        global monitored_thread_map
        monitored_thread_map[ct_name] = MonitoredThread()

    def calc_run_time(self):
        cur_time = datingdays.now().timestamp()
        return "%0.2f" % (cur_time - self.start_time)

    def run(self):
        global monitored_thread_map
        global monitor_lock
        specified_frequency = -1
        for thread_name in self.process_map.keys():
            ct_kwargs = self.process_map[thread_name]
            if 'frequency' in ct_kwargs:
                specified_frequency = ct_kwargs.pop('frequency')
        frequency = specified_frequency if specified_frequency > 0 else 5
        running = True
        while running:
            time.sleep(frequency)
            print(''.join((datingdays.now().strftime('%a %b %d %H:%M:%S.%f')[:-4],
                           ': mem(', mem_info(),
                           ') runtime(', self.calc_run_time(), ')')))
            with monitor_lock:
                for thread_name in self.process_map.keys():
                    ct_kwargs = self.process_map[thread_name]
                    my_mt = get_monitored_thread(thread_name)
                    msg = ''.join(('   ', thread_name, ':'))
                    for k in ct_kwargs.keys():
                        method = ct_kwargs[k]
                        msg = ''.join((msg, ' ', k, ':', str(method())))
                    if len(my_mt.monitor_timer_map) > 0:
                        msg = ''.join((msg, ' cur_meth:',
                                       my_mt.monitor_current_method, '(',
                                       str(len(my_mt.monitor_call_stack)), ')'))
                    print(msg)
                    for _key in my_mt.monitor_timer_map.keys():
                        _val = my_mt.monitor_timer_map[_key]
                        print('\t', _key, ' ', _val)


singleton = None


def get_singleton(**kwargs):
    global singleton
    if singleton is None:
        singleton = Monitor(**kwargs)
        print('Constructed NEW (singleton) Monitor instance')
    else:
        print('Appending kwargs to existing Monitor instance')
        singleton.add_thread(**kwargs)
    return singleton


class MultiprocessMonitor:
    def __init__(self, lock, **kwargs):
        with lock:
            self.single = get_singleton(**kwargs)


def get_test_one():
    return 1.23


def get_test_two():
    return tuple(['one', 2, 5.0])


class Calculator:
    @timeit
    def calculate_something(self, num):
        """
        an example function that returns sum of all numbers up to the square of num
        """
        total = sum((x for x in range(0, num**2)))
        return total

    def __repr__(self):
        return f'calc_object:{id(self)}'


def main():
    global monitored_thread_map
    m = Monitor(frequency=2, first=get_test_one, second=get_test_two)
    c = Calculator()
    c.calculate_something(100)
    print('one down')
    c.calculate_something(2500)
    c.calculate_something(5000)
    c.calculate_something(10000)
    print(monitored_thread_map)
    time.sleep(2000)
    print('Bye!')


if __name__=="__main__":
    main()
