import os
import sys
from socket import gethostname
import requests
import time


def fetch_json_value(key, json):
    cur_json = json
    split = key.split('.')
    if len(split) > 1:
        for k in split:
            cur_json = fetch_json_value(k, cur_json)
        return cur_json
    else:
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
        self.MAX_LOOPS = 6
        with open('./web3.github.token', 'r') as f:
            self.token = f.readline()
            self.token = self.token.strip('\n')
            self.headers = {'Authorization': 'token %s' % self.token}

    def get_stats(self):
        return ' '.join(('GEIO:',
                         str(self.good_reply_code_count), ',',
                         str(self.error_count), ',',
                         str(self.incomplete_count), ',',
                         str(self.overload_count)))

    def fetch_with_lock(self, url):
        try:
            self.git_hub_lock.acquire()
            time.sleep(1)
            return requests.get(url, headers=self.headers)
        except Exception as e:
            print('Error encountered calling', url, e)
            return None
        finally:
            self.git_hub_lock.release()

    def fetch_json_with_lock(self, url, recurse_count=0):
        json_ret_val = None
        reply = self.fetch_with_lock(url)

        if reply is None:
            self.error_count += 1
            print('No response received from API call to GitHub', url)
        elif reply.status_code == 403:
            self.overload_count += 1
            # We've exceed our 5000 calls per hour!
            print('Maximum calls/hour exceeded! Sleeping', recurse_count, 'minute(s)')
            print('Working on', url)
            time.sleep(60*recurse_count)
            if recurse_count <= self.MAX_LOOPS:
                json_ret_val = self.fetch_json_with_lock(url, recurse_count+1)
        elif reply.status_code == 202:
            self.incomplete_count += 1
            print('GitHub is "still working on"', url)
            time.sleep(30*(recurse_count+1))
            if recurse_count <= self.MAX_LOOPS:
                json_ret_val = self.fetch_json_with_lock(url, recurse_count+1)
        elif reply.status_code == 200:
            try:
                self.good_reply_code_count += 1
                json_ret_val = reply.json()
            except requests.exceptions.JSONDecodeError as e:
                print('Error encountered parsing reply from',url,e)
        else:
            self.error_count += 1
            print('ERROR - Status code:', reply.status_code, 'encountered ', url)

        return json_ret_val

