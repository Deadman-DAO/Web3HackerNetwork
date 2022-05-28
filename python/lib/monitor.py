import os
import threading
import time
from pytz import timezone
from datetime import datetime as datingdays


def concat(*args):
    ret_val = ''
    for n in args:
        ret_val = ret_val + (n if isinstance(n, str) else str(n))
    return ret_val


class Monitor:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        frequency = self.kwargs.pop('frequency', 5)
        running = True
        while running:
            time.sleep(frequency)
            msg = datingdays.now().strftime('%a %b %d %H:%M:%S.%f')[:-4]+':'
            for k in self.kwargs.keys():
                method = self.kwargs.get(k)
                t = concat(msg, ' ', k, ':', method())
                msg = t
            print(msg)


def get_test_one():
    return 1.23


def get_test_two():
    return tuple(['one', 2, 5.0])


def main():
    m = Monitor(frequency=2, first=get_test_one, second=get_test_two)
    time.sleep(2000)
    print('Bye!')


if __name__=="__main__":
    main()
