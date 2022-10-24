from threading import Thread, current_thread, Lock
from log_trial import log

my_variable = None

lock = Lock()


def get_my_variable():
    global my_variable
    if not my_variable:
        with lock:
            try:
                if not my_variable:
                    log('Constructing my_variable for the first time')
                    my_variable = 0
                else:
                    log('That variable was already defined')
            except Exception as e:
                print("I'm not sure what happened here.  Good point for debugging")
    my_variable += 1
    return my_variable


