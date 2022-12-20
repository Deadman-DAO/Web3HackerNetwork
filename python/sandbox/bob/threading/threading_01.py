from time import sleep, perf_counter
from threading import Thread

def task(task_id):
    duration = 1
    print(f'thread {task_id} sleeping for {duration}...')
    sleep(duration)
    print(f'thread {task_id} is done')

threads = list()
for i in range(10):
    threads.append(Thread(target=task, args=(i+1,)))

start_time = perf_counter()
for thread in threads: thread.start()
for thread in threads: thread.join()
end_time = perf_counter()
print(f'It took {end_time - start_time: 0.2f} seconds to complete')
