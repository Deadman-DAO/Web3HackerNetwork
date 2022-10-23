import sys
import os
from lib.monitor import timeit
from lib.repo_analyzer import RepoAnalyzer
import __init__

print("Path:")
for path in sys.path:
    print(path)

print("Here's where I am: "+sys.path[0])


@timeit
def do_something():
    print("Doing something")


do_something()
