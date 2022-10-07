import random
from asyncio import sleep


def execute_analysis(owner=None, repo_name=None, numstat=None, repo_path=None):
    sleepy_time = random.Random().random() * 10
    print('#TST Executing analysis for {0}/{1} sleeping {3}'.format(owner, repo_name, sleepy_time))
    sleep(sleepy_time)
    print('#TST Finished analysis for {0}/{1}'.format(owner, repo_name))
