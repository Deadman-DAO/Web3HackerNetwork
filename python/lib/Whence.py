import os
import pathlib

import sys


class Whence:
    def __init__(self, path):
        self.path = pathlib.Path(path)

    def main(self):
        if self.path is None:
            print('No filename provided')
            sys.exit(1)
        print("Searching for '{}'".format(self.path))
        for pstr in os.environ['PATH'].split(';' if os.name == 'nt' else ':'):
            p = pathlib.Path(pstr)
            if p.exists() and p.is_dir():
                if pathlib.Path(p, self.path).exists():
                    print(pathlib.Path(p, self.path))


if __name__ == "__main__":
    Whence(sys.argv[1]).main()
