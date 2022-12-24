from time import perf_counter
# from lib.monitor import MultiprocessMonitor, timeit
from lib.signal_handler import SignalHandler
import os
import sys
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

def get_blame(repo_dir, file_path):
    cmd = ['nice', 'git', '-C', repo_dir, 'blame', '--porcelain', file_path]
    handler = SignalHandler()
    success, stdout, stderr = handler.execute_os_cmd(cmd)
    stdout = str(stdout)
    stdout = re.sub('^b"', '', stdout)
    stdout = re.sub("^b'", '', stdout)
    stdout = re.sub('"$', '', stdout)
    stdout = stdout.replace('\\n', '\n')
    stdout = stdout.replace('\\t', '\t')
    return stdout

class BlameGameRetriever():
    def __init__(self):
        self.repo_dir = \
            '/home/bob/projects/sample/pavanpoojary7/Sports-Tournaments'

        paths_file = \
            '/home/bob/projects/sample/pavanpoojary7/js_files.txt'
        with open(paths_file, 'rt') as paths_in:
            self.paths = [line.strip() for line in paths_in.readlines()]
        print(f'File Count: {len(self.paths)}')

    def do_it(self, path):
        commit_lines_regex = re.compile('^([0-9a-f]{40}) [0-9]+ [0-9]+ ([0-9]+)$')
        gather_name_regex = re.compile('^author (.*)$')
        gather_mail_regex = re.compile('^author-mail (.*)$')
        text = get_blame(self.repo_dir, path)
        lines = text.splitlines(False)
        seek_commit_mode = True
        gather_mode = False
        commits = dict()
        for line in lines:
            if seek_commit_mode:
                commit_lines_matches = commit_lines_regex.findall(line)
                if commit_lines_matches:
                    commit_id = commit_lines_matches[0][0]
                    line_count = int(commit_lines_matches[0][1])
                    if commit_id in commits:
                        commit = commits[commit_id]
                        commit['line_count'] += line_count
                    else:
                        seek_commit_mode = False
                        gather_mode = True
                        name = None
                        mail = None
            elif gather_mode:
                if not name:
                    name_match = gather_name_regex.match(line)
                    if name_match:
                        name = name_match[0]
                elif not mail:
                    mail_match = gather_mail_regex.match(line)
                    if mail_match:
                        mail = mail_match[0]
                if name and mail:
                    commits[commit_id] = {
                        'name':name,
                        'email':mail,
                        'line_count':line_count
                    }
                    seek_commit_mode = True
                    gather_mode = False
        committers = dict()
        for commit_id, commit in commits.items():
            name = commit['name']
            email = commit['email']
            author = f'{name} <{email}>'
            if author not in committers:
                committers[author] = {'line_count':0, 'commit_count':0}
            committers[author]['line_count'] += commit['line_count']
            committers[author]['commit_count'] += 1
        return (path, committers)

    def do_it_with_files(self):
        paths = self.paths[0:1000]
        print(f'processing {len(paths)} files')
        with ThreadPoolExecutor(max_workers=10) as executor:
            threadmap = executor.map(self.do_it, paths)
        for result in threadmap:
            print(f'{result}')
        
if __name__ == '__main__':
    bgr = BlameGameRetriever()
    bgr.do_it_with_files()
