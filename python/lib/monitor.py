import os
import threading
import time
from pytz import timezone
from datetime import datetime as datingdays


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
            msg = datingdays.now().strftime('%a %b %d %H:%M:%S.')
            for k in self.kwargs.keys():
                method = self.kwargs.get(k)
                msg = msg + ' ' + k + ':' + method()
            print(msg)


def get_test_one():
    return 'Hello'


def get_test_two():
    return 'Universe'


def main():
    m = Monitor(frequency=2, first=get_test_one, second=get_test_two)
    time.sleep(20)
    print('Bye!')


if __name__=="__main__":
    main()
