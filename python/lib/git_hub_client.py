import os
import threading
import sys
from socket import gethostname
import requests
import time
from datetime import datetime as dt


def fetch_json_value(key, json):
    if key in json:
        return json[key]
    raise StopIteration(''.join(('key ', key, ' not found.')))


class GitHubClient:
    def __init__(self, git_hub_lock):
        self.git_hub_lock = git_hub_lock
        self.machine_name = os.uname().nodename if sys.platform != "win32" else gethostname()
        self.error_count = 0
        self.overload_count = 0
        self.incomplete_count = 0
        self.good_reply_code_count = 0
        self.MAX_LOOPS_FOR_THROTTLING = 6
        self.MAX_LOOPS_FOR_202_CONDITION = 3
        self.html_reply = None
        self.json_reply = None
        self.fetch_with_lock_reply = None
        self.longest_wait = 0
        with open('./web3.github.token', 'r') as f:
            self.token = f.readline()
            self.token = self.token.strip('\n')
            self.headers = {'Authorization': 'token %s' % self.token}

    def get_stats(self):
        return ','.join(('GEIO:',
                         str(self.good_reply_code_count),
                         str(self.error_count),
                         str(self.incomplete_count),
                         str(self.overload_count)))

    def fetch_with_lock(self, url):
        self.fetch_with_lock_reply = None
        with self.git_hub_lock:
            time.sleep(1)
            self.fetch_with_lock_reply = requests.get(url, headers=self.headers)

        return self.fetch_with_lock_reply

    def fetch_json_with_lock(self, url, recurse_count=0):
        self.json_reply = None
        start_time = dt.now().timestamp()
        with self.git_hub_lock:
            elapsed = dt.now().timestamp() - start_time;
            if elapsed > self.longest_wait:
                self.longest_wait = elapsed
                print('%0.3f new max time for thread ' % elapsed, threading.current_thread().name)
            time.sleep(1)
            self.html_reply = requests.get(url, headers=self.headers)
            if self.html_reply is not None and self.html_reply.status_code == 200:
                self.json_reply = self.html_reply.json()

        if self.html_reply is None:
            self.error_count += 1
            print('No response received from API call to GitHub', url)
        elif self.html_reply.status_code == 403:
            self.overload_count += 1
            # We've exceed our 5000 calls per hour!
            print('Maximum calls/hour exceeded! Sleeping', recurse_count, 'minute(s)')
            print('Working on', url)
            time.sleep(60*(recurse_count+1))
            if recurse_count < self.MAX_LOOPS_FOR_THROTTLING:
                self.json_reply = self.fetch_json_with_lock(url, recurse_count+1)
        elif self.html_reply.status_code == 202:
            self.incomplete_count += 1
            print('GitHub is "still working on"', url)
            time.sleep(30*(recurse_count+1))
            if recurse_count < self.MAX_LOOPS_FOR_202_CONDITION:
                self.json_reply = self.fetch_json_with_lock(url, recurse_count+1)
                print(hex(threading.current_thread().native_id),threading.current_thread().name,'returning ',
                      'VALID' if self.json_reply is not None else 'JUNK', 'from post_202 fetch_json_with_lock')
        elif self.html_reply.status_code == 200:
            self.good_reply_code_count += 1
        else:
            self.error_count += 1
            print('ERROR - Status code:', self.html_reply.status_code, 'encountered ', url)

        return self.json_reply

