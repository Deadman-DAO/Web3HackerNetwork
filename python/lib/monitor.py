import os
from datetime import datetime as datingdays
from functools import wraps
from threading import Thread, current_thread, Lock

import psutil
import time
from sys import argv

monitored_thread_map = {}
monitor_lock = Lock()


def find_argv_param(key, default_val=None):
    ret_val = default_val
    for n in argv:
        kv = n.split('=')
        if len(kv) > 1 and kv[0] == key:
            ret_val = kv[1]
    return ret_val


def concat(*args):
    ret_val = ''
    for n in args:
        ret_val = ret_val + (n if isinstance(n, str) else str(n))
    return ret_val


def align_columns(array_of_tuples, prefix=None):
    try:
        max_col_width = []
        for row in array_of_tuples:
            for idx in range(len(row)):
                if len(max_col_width) <= idx:
                    max_col_width.append(0)
                if max_col_width[idx] < len(str(row[idx])):
                    max_col_width[idx] = len(str(row[idx]))
        for row in array_of_tuples:
            line = prefix if prefix else ''
            for idx in range(len(row)):
                line += f'{row[idx]:>{max_col_width[idx]+1}}'
            print(line)
    except Exception as e:
        print('WTF?', e)


class Tracker:
    def __init__(self):
        self.call_count = 0
        self.exec_time = 0

    def __str__(self):
        return concat('call_count:',self.call_count,' exec_time:', f'{self.exec_time: 0.3f}')

    def tuple(self):
        return 'call_count:', str(self.call_count), 'exec_time:', f'{self.exec_time: 0.3f}'


class MonitoredThread(object):
    def __init__(self):
        self.monitor_timer_map = {}
        self.monitor_current_method = ''
        self.monitor_call_stack = []
        self.start_time = 0
        self.result = None
        self.end_time = 0
        self.tracker = None




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
        self.thread_id_map = {}
        self.add_thread(**kwargs)
        self.process = Thread(target=self.run, daemon=True, name='Monitor')
        self.process.start()
        self.start_time = datingdays.now().timestamp()

    def add_thread(self, **kwargs):
        ct_name = current_thread().name
        self.process_map[ct_name] = kwargs.copy()
        self.process_map[ct_name].pop('web_lock', None)
        self.process_map[ct_name].pop('database_lock', None)
        self.thread_id_map[ct_name] = current_thread().ident
        global monitored_thread_map
        monitored_thread_map[ct_name] = MonitoredThread()

    def add_display_methods(self, **kwargs):
        ct_name = current_thread().name
        ct_kwargs = self.process_map[ct_name] if ct_name in self.process_map else None
        if ct_kwargs:
            ct_kwargs.update(kwargs)

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
            if 'web_lock' in ct_kwargs:
                print('Removing web_lock')
                ct_kwargs.pop('web_lock')
            if 'database_lock' in ct_kwargs:
                print('Removing database_lock')
                ct_kwargs.pop('database_lock')
        frequency = specified_frequency if specified_frequency > 0 else 5
        running = True
        while running:
            time.sleep(frequency)
            try:
                print(''.join((datingdays.now().strftime('%a %b %d %H:%M:%S.%f')[:-4],
                               ': mem(', mem_info(),
                               ') runtime(', self.calc_run_time(), ')')))
                with monitor_lock:
                    for thread_name in self.process_map.keys():
                        ct_kwargs = self.process_map[thread_name]
                        my_mt = get_monitored_thread(thread_name)
                        thread_id = self.thread_id_map[thread_name]
                        msg = ''.join(('   ', thread_name, '[', str(thread_id), ']:'))
                        remove_key_list = []
                        for k in ct_kwargs.keys():
                            method = ct_kwargs[k]
                            if not callable(method):
                                print(k, method, ' is NOT callable.  Removing it.')
                                remove_key_list.append(k)
                            else:
                                msg = ''.join((msg, ' ', k, ':', str(method())))
                        for remove in remove_key_list:
                            ct_kwargs.pop(remove)
                        if len(my_mt.monitor_timer_map) > 0:
                            msg = ''.join((msg, ' cur_meth:',
                                           my_mt.monitor_current_method, '(',
                                           str(len(my_mt.monitor_call_stack)), ')'))
                        print(msg)
                        array = []
                        for _key in my_mt.monitor_timer_map.keys():
                            array.append((_key,)+my_mt.monitor_timer_map[_key].tuple())
                        align_columns(array, prefix='\t')
            except Exception as e:
                print('Monitor encountered error:', e)


simpleton_lock = Lock()
singleton = None


def get_singleton(**kwargs):
    global singleton
    global simpleton_lock
    if singleton is None:
        with simpleton_lock:
            if singleton is None:
                singleton = Monitor(**kwargs)
                print('Constructed NEW (singleton) Monitor instance')
            else:
                print('Simpleton locking prevented dual Monitor instances')
    else:
        print('Appending kwargs to existing Monitor instance')
        singleton.add_thread(**kwargs)
    return singleton


class MultiprocessMonitor:
    def __init__(self, **kwargs):
        print('MultiprocessMonitor().__init__', kwargs)
        self.single = get_singleton(**kwargs)


