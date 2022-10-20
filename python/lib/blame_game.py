from monitor import MultiprocessMonitor, timeit
from signal_handler import SignalHandler
import os
import sys
import re


class BlameGameRetriever(SignalHandler):
    def __init__(self, repo_dir):
        SignalHandler().__init__()
        self.repo_dir = repo_dir
        self.success = False
        self.stdout = None
        self.stderr = None
        self.max_wait = 60

    @timeit
    def get_blame_game(self, filename):
        name_array = self.run_blame(filename, '-l')
        email_array = self.run_blame(filename, '-le')
        if len(name_array) != len(email_array):
            raise Exception('Name and email arrays are not the same length')
        result = {}
        for i in range(len(name_array)):
            cuple = '\t'.join((name_array[i], email_array[i]))
            if cuple in result:
                result[cuple] += 1
            else:
                result[cuple] = 1
        return result

    @timeit
    def run_blame(self, filename, blame_params) -> dict:
        contribution_array = []
        full_name = os.path.join(self.repo_dir, filename)
        if not os.path.exists(full_name):
            return None
        cmd = ['nice',  'git', '-C', self.repo_dir, 'blame', blame_params, filename]

        if sys.platform == "win32":
            # Take out the first element of the cmd array as windows isn't "nice"
            cmd = cmd[1:]
        self.success, self.stdout, self.stderr = self.execute_os_cmd(cmd)
        if self.success is not None and self.success is True and self.stdout is not None:
            line_count = 0.0
            try:
                self.stdout = self.stdout.decode('utf-8')

                for line in self.stdout.split('\n'):
                    array = re.findall('^[\^a-f0-9A-F]+\s+[^\(]*\((.*?) [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} ', line)
                    if len(array) > 1:
                        print('Error:  More than one match found in line:  ', line)
                    elif len(array) < 1:
                        print('Error:  No match found in line:  ', line)
                    else:
                        contribution_array.append(array[0])
            except Exception as e:
                print('Error processing blame output:', e)
            return contribution_array


if __name__ == '__main__':
    print(str(BlameGameRetriever('.').get_blame_game('./blame_game.py')))
