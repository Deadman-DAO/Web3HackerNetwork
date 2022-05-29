import os
import threading
import time
from pytz import timezone
from datetime import datetime as datingdays
from functools import wraps


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


monitor_timer_map = {}
monitor_current_method = ''
monitor_call_stack = []


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        global monitor_current_method
        global monitor_timer_map
        global monitor_call_stack
        monitor_current_method = func.__name__;
        monitor_call_stack.insert(0, monitor_current_method)
        start_time = datingdays.now().timestamp()
        result = func(*args, **kwargs)
        end_time = datingdays.now().timestamp()
        total_time = end_time - start_time
        t = monitor_timer_map[func.__name__] if func.__name__ in monitor_timer_map  else None
        if t is None:
            t = Tracker()
            monitor_timer_map[func.__name__] = t
        t.call_count += 1
        t.exec_time += total_time
        monitor_call_stack.remove(monitor_call_stack[0])
        monitor_current_method = monitor_call_stack[0] if len(monitor_call_stack > 0) else 'Unknown!'
        return result
    return timeit_wrapper


class Monitor:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        global monitor_current_method
        global monitor_timer_map
        global monitor_call_stack
        frequency = self.kwargs.pop('frequency', 5)
        running = True
        while running:
            time.sleep(frequency)
            msg = datingdays.now().strftime('%a %b %d %H:%M:%S.%f')[:-4]+':'
            for k in self.kwargs.keys():
                method = self.kwargs.get(k)
                t = concat(msg, ' ', k, ':', method())
                msg = t
            if len(monitor_timer_map) > 0:
                msg = concat(msg, ' cur_meth:', monitor_current_method, '(', len(monitor_call_stack), ')')
            print(msg)
            for t in monitor_timer_map.keys():
                tm = monitor_timer_map.get(t)
                print('\t', t, ' ', tm)


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
    m = Monitor(frequency=2, first=get_test_one, second=get_test_two)
    c = Calculator()
    c.calculate_something(100)
    print('one down')
    c.calculate_something(2500)
    c.calculate_something(5000)
    c.calculate_something(10000)
    print(monitor_timer_map)
    time.sleep(2000)
    print('Bye!')


if __name__=="__main__":
    main()
