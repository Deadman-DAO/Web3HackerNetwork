import sys
from lib.monitor import timeit

print("Path:")
for path in sys.path:
    print(path)

print("Here's where I am: "+sys.path[0])


@timeit
def do_something():
    print("Doing something")


do_something()
