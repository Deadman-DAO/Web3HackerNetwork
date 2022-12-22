from lib.monitor import MultiprocessMonitor, timeit
from lib.signal_handler import SignalHandler
import os
import sys
import time
from abc import ABC, abstractmethod
from datetime import datetime as datingdays, timedelta
import pytz
from enum import Enum
import traceback
from threading import Lock

class PerformanceMonitor:
    def __init__(self):
        self.call_count = 0
        self.exec_time = 0
        self.compute_time = 0
        self.lock = Lock()
        self.start_time = time.time()

    def report_performance(self, start_time, exec_finish_time, compute_finish_time):
        print_it = False
        with self.lock:
            self.call_count += 1
            self.exec_time += (exec_finish_time - start_time)
            self.compute_time += (compute_finish_time - exec_finish_time)
            if self.call_count % 100 == 0:
                print_it = True
        if print_it:
            print(f'Blame files processed: {self.call_count} git exec time: {self.exec_time: 0.3f} '+
                  f'compute time: {self.compute_time: 0.3f} '+
                  f'actual passed time: {(time.time() - self.start_time): 0.3f}')

simpleton = PerformanceMonitor()

class LineHandler(ABC):
    @abstractmethod
    def process_line(self, line, handler_map = None):
        pass

class HandlerType(Enum):
    AUTHOR = 'a'
    COMMITTER = 'c'
    PREVIOUS = 'p'
    SUMMARY = 's'
    FILENAME = 'f'
    SOURCE = '\t'
    HASH = 'h'
    MOM  = 'm'

class HackerTracker:
    def __init__(self, time_zone):
        self.lines_contributed = 0
        self.author_hash_map = {}
        self.commit_hash_map = {}
        self.time_zone = time_zone
        self.min_epoch = None
        self.max_epoc = None

    def add_line(self, commit_hash, epoch, committer_only = False):
        self.lines_contributed += 1
        self.min_epoch = epoch if self.min_epoch is None else min(self.min_epoch, epoch)
        self.max_epoc = epoch if self.max_epoc is None else max(self.max_epoc, epoch)
        dic = self.author_hash_map
        if committer_only:
            dic = self.commit_hash_map

        if commit_hash in dic:
            dic[commit_hash] += 1
        else:
            dic[commit_hash] = 1

    def __str__(self):
        return f'lines contributed: {self.lines_contributed} commits made: {len(self.author_hash_map)}'

class SourceLine(LineHandler):
    def __init__(self):
        self.source = []
        self.hacker_tracker_map = {}

    def process_line(self, line, handler_map = None):
        self.source.append(line)
        if handler_map:
            hacker = handler_map[HandlerType.AUTHOR.value]
            committer = handler_map[HandlerType.COMMITTER.value]
            hacker_key = hacker.get_name_email_key()
            committer_key = committer.get_name_email_key()

            if hacker.get_name_email_key() not in self.hacker_tracker_map:
                self.hacker_tracker_map[hacker_key] = HackerTracker(hacker.time_zone_str)
            self.hacker_tracker_map[hacker_key]. \
                add_line(handler_map[HandlerType.HASH.value].get_commit_hash(), hacker.epoch)
            if committer_key != hacker_key:
                if committer_key not in self.hacker_tracker_map:
                    self.hacker_tracker_map[committer_key] = HackerTracker(committer.time_zone_str)
                self.hacker_tracker_map[committer_key]. \
                    add_line(handler_map[HandlerType.HASH.value].get_commit_hash(), committer.epoch, True)


class Commit(LineHandler):
    def __init__(self):
        self.hash = None
        self.prev_line_num = -1
        self.current_line_num = -1
        self.lines_within_commit = -1

    def get_commit_hash(self):
        return self.hash

    def process_line(self, line, handler_map = None):
        try:
            self.hash = line[:40]
            nums = line[41:].split(' ')
            self.prev_line_num = int(nums[0])
            self.current_line_num = int(nums[1])
            if len(nums) > 2:
                self.lines_within_commit = int(nums[2])
        except Exception as e:
            print(f'Error processing commit line: {line} error: {e}')
            print(f'File name: {handler_map[HandlerType.FILENAME.value].file_name} line number: {len(handler_map[HandlerType.SOURCE.value].source)}')

class Summary(LineHandler):
    def __init__(self):
        self.comment = None

    def process_line(self, line, handler_map = None):
        self.comment = line[len('summary '):]

class Previous(LineHandler):
    def __init__(self):
        self.commit = None
        self.file_name = None

    def process_line(self, line, handler_map = None):
        la = line.split(' ')
        self.commit = la[1]
        self.file_name = la[2]

class FileName(LineHandler):
    def __init__(self):
        self.file_name = None

    def process_line(self, line, handler_map = None):
        self.file_name = line[len('filename '):]

class Hacker(LineHandler):
    def __init__(self, prefix):
        self.name = None
        self.email = None
        self.time = None
        self.orig_time_zone_hours = 0
        self.orig_time_zone_minutes = 0
        self.orig_time_operator = 1
        self.prefix = prefix
        self.target_tz = pytz.timezone('UTC')
        self.time_zone_str = None
        self.epoch = None

    def get_name_email_key(self):
        return self.name + ' ' + '{'+self.email+'}'

    def process_line(self, line, handler_map = None):
        if line and line.startswith(self.prefix):
            line = line[len(self.prefix):]
            if line[0] == ' ':
                self.name = line[1:]
            elif line.startswith('-mail'):
                self.email = line[7:len(line) - 1]
            elif line.startswith('-time'):
                self.epoch = int(line[6:])
                self.time = datingdays.fromtimestamp(self.epoch, tz=self.target_tz)
            elif line.startswith('-tz'):
                self.time_zone_str = line[4:]
                self.orig_time_operator = 1 if line[4] == '+' else -1
                self.orig_time_zone_hours = int(line[5:7])
                self.orig_time_zone_minutes = int(line[8:10])
                # No need to adjust the UTC time - The fromtimestamp seems to do that already
#                self.time = self.time - self.orig_time_operator * timedelta(hours=self.orig_time_zone_hours, minutes=self.orig_time_zone_minutes)
        else:
            print("Error - This line doesn't start with "+self.prefix+"\n"+line)


class BlameGameRetriever(SignalHandler):
    def __init__(self, repo_dir):
        SignalHandler().__init__()
        global simpleton
        self.repo_dir = repo_dir
        self.success = False
        self.stdout = None
        self.stderr = None
        self.max_wait = 60
        self.user_map = {}
        self.be_nice = self.get_env_var('BE_NICE', 'True', self.boolean_damnit)
        self.commit = Commit()
        self.exec_map = {HandlerType.AUTHOR.value: Hacker('author'),
                         HandlerType.COMMITTER.value: Hacker('committer'),
                         HandlerType.PREVIOUS.value: Previous(),
                         HandlerType.SUMMARY.value: Summary(),
                         HandlerType.FILENAME.value: FileName(),
                         HandlerType.SOURCE.value: SourceLine(),
                         HandlerType.HASH.value: self.commit,
                         HandlerType.MOM.value: self}

    def is_hex(self, hash) -> bool:
        try:
            int(hash, 16)
            return True
        except ValueError:
            return False

    @timeit
    def get_blame_game(self, filename):
        self.run_blame(filename, '--porcelain')
        return self.exec_map[HandlerType.SOURCE.value].hacker_tracker_map

    @timeit
    def run_blame(self, filename, blame_params) -> dict:
        if not os.path.exists(os.path.join(self.repo_dir, filename)):
            return None
        cmd = ['nice',  'git', '-C', self.repo_dir, 'blame', blame_params, filename]

        if sys.platform == "win32" or not self.be_nice:
            # Take out the first element of the cmd array as windows isn't "nice"
            cmd = cmd[1:]
        start_time = time.time()
        self.success, self.stdout, self.stderr = self.execute_os_cmd(cmd)
        end_time = time.time()
        #print(filename+ " took " + str(end_time - start_time) + " seconds to generate the blame")
        if self.success is not None and self.success is True and self.stdout is not None:
            try:
                self.stdout = self.stdout.decode('utf-8')
                lines = self.stdout.split('\n')
                done = False
                #print("Processing "+str(len(lines))+" lines")
                for line in lines:
                    test_split = line.split(' ')
                    if len(test_split[0]) == 40 and len(test_split) > 2 and self.is_hex(test_split[0]):
                        self.commit.process_line(line, self.exec_map)
                    elif len(line) < 1:
                        if not done:
                            done = True
                        else:
                            print('Unexpected blank line encounted')
                    elif line[0] in self.exec_map:
                        self.exec_map[line[0]].process_line(line, self.exec_map)
                    else:
                        print("Error - This line doesn't start with an expected character [a,c,p,s,f,<tab>]\n"+line)
                more_time = time.time()
                simpleton.report_performance(start_time, end_time, more_time)
#                print(filename+ " took " + str(more_time - end_time) + " seconds to process the blame")
            except Exception as e:
                print('Error processing blame output:', e)
                traceback.print_exc()


if __name__ == '__main__':
    #map = BlameGameRetriever('./repos/u-root/u-root').get_blame_game('u-root.go')
    map = BlameGameRetriever('../python/lib').get_blame_game('repo_numstat_gatherer.py')
    for key, val in map.items():
        print(key, val)

