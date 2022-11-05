import logging
from logging.handlers import RotatingFileHandler as log_rfh
import sys
import traceback

import w3hn.log.log_init as log_init_alias

initialized = False
default_log_dir = '/opt/deadman/Web3HackerNetwork/log'

# This will add a new handler, retaining existing handlers. Only call
# this if you are the entry point of the program. If you are a library,
# not the main entry point, you should just call "logger(...)".
#
# Input Params:
# log_dir_path = defaults to the default logging dir, None = write to stdout
def initialize(log_dir_path=default_log_dir):
    log_init_alias.initalized = True
    root_log = logging.getLogger()
    root_log.setLevel(logging.DEBUG)
    if log_dir_path is None:
        handler = logging.StreamHandler(sys.stdout)
    else:
        log_path = f'{log_dir_path}/w3hn.log'
        try:
            handler = log_rfh(log_path, mode='a', backupCount=9)
            handler.doRollover()
        except:
            handler = log_rfh(log_path, mode='w', backupCount=9)
            handler.doRollover()
    handler.setLevel(logging.DEBUG)
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    root_log.addHandler(handler)
    for noisy in ['boto3', 'botocore', 'urllib3', 'matplotlib']:
        logging.getLogger(noisy).setLevel(logging.WARNING)
    logging.getLogger('log_init').info(f'initialize({log_dir_path})')

# This will not add a handler.
# To explicitly add a new handler, call initialize.
#
# Input Params:
# name = the name of the logger, will be shown in the log
# log_dir_path = defaults to the default logging dir, None = write to stdout
def logger(name, log_dir_path=default_log_dir):
    # if not log_init_alias.initialized:
    #     initialize(log_dir_path)
    logging.getLogger('log_init').info(f'logger({name}, {log_dir_path})')
    return logging.getLogger(name=name)

if __name__ == '__main__':
    log = log_init_alias.logger(__file__, None)
    log.warning("warning to stdout")
    log_init_alias.initialize('./')
    log.warning("warning to stdout and ./ file")
    log_init_alias.initialize()
    log.warning("warning to stdout, ./ file, and default file")
    try:
        a = 1/0
    except:
        log.exception("dividing by zero threw an exception")
    log.info("the system didn't die, that exception was handled")

