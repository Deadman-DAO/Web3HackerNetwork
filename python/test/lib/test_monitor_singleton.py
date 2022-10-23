from concurrent.futures import ThreadPoolExecutor as tpe
from lib.monitor import MultiprocessMonitor

with tpe() as exec:
    meaningless = [1, 2, 3, 4, 5]
    exec.map(MultiprocessMonitor.__init__, meaningless)

print('All done')