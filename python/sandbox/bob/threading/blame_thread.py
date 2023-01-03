from lib.monitor import MultiprocessMonitor, timeit
from lib.signal_handler import SignalHandler
import os
import sys
import re

repo_dir = '/home/bob/projects/Web3HackerNetwork'
file_path = 'sandbox/notebooks/matt/new_repos.json'
# file_path = '.gitignore'
file_path = 'python/w3hn/dependency/java.py'

class BlameGameRetriever(SignalHandler):
    def __init__(self):
        SignalHandler.__init__(self)

    def get_blame(self):
        cmd = ['nice', 'git', '-C', repo_dir, 'blame', '--porcelain', file_path]

        if sys.platform == "win32":
            # Take out the first element of the cmd array as windows isn't "nice"
            cmd = cmd[1:]
        self.success, self.stdout, self.stderr = self.execute_os_cmd(cmd)
        self.stdout = str(self.stdout).replace('\\n', '\n')
        self.stdout = str(self.stdout).replace('\\t', '\t')
        return self.stdout

    def do_it(self):
        text = self.get_blame()
        lines = text.splitlines(False)
        for line in lines:
            commit_lines_regex = '^([0-9a-f]{40}) [0-9]+ [0-9]+ ([0-9]+)$'
            commit_lines_matches = re.findall(commit_lines_regex, line)
            if (commit_matches):
                # print(f'{matches}')
                commit_id = commit_matches[0][0]
                line_count = int(commit_matches[0][1])
                print(f'{commit_id} {line_count}')
            matches = 

    def do_it_forever(self):
        while True:
            self.do_it()
        
if __name__ == '__main__':
    bgr = BlameGameRetriever()
    bgr.do_it()

# 1cb814867f835233bf735faf2550851c8ce8efa9 14 19 6
# author enigmatt
# author-mail <git@theenkes.com>
# author-time 1666043270
# author-tz -0700
# committer enigmatt
# committer-mail <git@theenkes.com>
# committer-time 1666043270
# committer-tz -0700
# summary Converting "file = open(blarg, \'r\')" with "with open(blarg, \'r\') as file:" to avoid leaving orphan files open.
# previous 5cc7d5466ee68590beb6c4c48904c6ab16f492d4 python/w3hn/dependency/java.py
# filename python/w3hn/dependency/java.py
# 	        with open(path, \'r\') as source:
