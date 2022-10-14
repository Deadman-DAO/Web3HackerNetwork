from monitor import MultiprocessMonitor, timeit
from signal_handler \
    import SignalHandler
import os
import sys
import re
from re import findall as bitty, split as squat


class BlameGameRetriever(SignalHandler):
    def __init__(self, repo_dir, commit_author_map):
        SignalHandler().__init__()
        self.repo_dir = repo_dir
        self.success = False
        self.stdout = None
        self.stderr = None
        self.commit_author_map = commit_author_map
        self.max_wait = 60

    @timeit
    def get_blame_game(self, filename, compiled_regex_pattern=None) -> (dict, list):
        hacker_contribution_map = {}
        dependency_list = []
        full_name = os.path.join(self.repo_dir, filename)
        if not os.path.exists(full_name):
            return None
        cmd = ['nice',  'git', '-C', self.repo_dir, 'blame', '-l', filename]

        if sys.platform == "win32":
            # Take out the first element of the cmd array as windows isn't "nice"
            cmd = cmd[1:]
        self.success, self.stdout, self.stderr = self.execute_os_cmd(cmd)
        if self.success is not None and self.success is True and self.stdout is not None:
            line_count = 0.0
            try:
                self.stdout = self.stdout.decode('utf-8')
                for line in self.stdout.split('\n'):
                    words = line.split(' ')
                    if len(words) > 0 and len(words[0]) == 40:
                        line_count += 1
                        who_when_line = line[42:].split(')')[0]
                        items = who_when_line.split(' ')

                        if compiled_regex_pattern:
                            source = line[len(line.split(')')[0])+2:]
                            for n in compiled_regex_pattern.findall(source):
                                if n not in dependency_list:
                                    if isinstance(n, tuple):
                                        dependency_list.append('.'.join(n) if n[0] else n[1])
                                    else:
                                        dependency_list.append(n)

                        if len(items) > 4:
                            line = int(items[len(items) - 1])
                            if words[1] in self.commit_author_map:
                                # commit hash found in commit_author_map
                                # retrieving author's md5sum
                                author_hash = self.commit_author_map[words[1]]
                                if author_hash not in hacker_contribution_map:
                                    hacker_contribution_map[author_hash] = 0
                                hacker_contribution_map[author_hash] += 1
            except Exception as e:
                print('Error processing blame output:', e)
            for key in hacker_contribution_map:
                hacker_contribution_map[key] = hacker_contribution_map[key] / (line_count if line_count > 0 else 1.0)
            return hacker_contribution_map, dependency_list


if __name__ == "__main__":
    ### Testing ###
    map = {}
    dir = '../'
    me = BlameGameRetriever(dir, map)
    reggy = re.compile("(?m)^(?:from[ ]+(\w+)[ ]+)?import[ ]+(\w+)(?:[ ]+as[ ]+\w+)?[ ]*$")
    dic, jane = me.get_blame_game('./python/lib/file_hacker_parquet.py', reggy)
    print(str(dic))
    print(str(jane))
    reggy = re.compile("(?m)^(?:from[ ]+(\w+)[ ]+)?import[ ]+(\w+)(?:[ ]+as[ ]+\w+)?[ ]*$")
    dic, jane = me.get_blame_game('./python/lib/blame_game.py', reggy)
    print(str(dic))
    print(str(jane))
    reggy = re.compile("^use ([^:^;]*)[;:].*$")
    dic, jane = me.get_blame_game('./sandbox/python/bob/main.rs', reggy)
    print(str(dic))
    print(str(jane))
    reggy = re.compile("^import ([^;]*);$")
    dic, jane = me.get_blame_game('./sandbox/python/bob/SpotifyApi.java', reggy)
    print(str(dic))
    print(str(jane))
