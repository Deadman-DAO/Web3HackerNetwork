import logging
from logging.handlers import RotatingFileHandler as log_rfh
import sys
import traceback

import w3hn.log.log_init as log_init

initialized = False
default_log_dir = '/opt/deadman/Web3HackerNetwork/log'

def initialize(log_dir_path=default_log_dir):
    root_log = logging.getLogger()
    root_log.setLevel(logging.DEBUG)
    if log_dir_path is None:
        handler = logging.StreamHandler(sys.stdout)
    else:
        handler = log_rfh(f'{log_dir_path}/w3hn.log', mode='w', backupCount=10)
        handler.doRollover()
    handler.setLevel(logging.DEBUG)
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    root_log.addHandler(handler)
    for noisy in ['boto3', 'botocore', 'urllib3', 'matplotlib']:
        logging.getLogger(noisy).setLevel(logging.WARNING)
    logging.getLogger('log_init').info(f'initialize({log_dir_path})')

# This will not add a handler it has already been initialized.
# To explicitly add a new handler, call initialize.
#
# Input Params:
# name = the name of the logger, will be shown in the log
# log_dir_path = defaults to the default logging dir, None = write to stdout
def logger(name, log_dir_path=default_log_dir):
    if not log_init.initialized:
        log_init.initialized = True
        initialize(log_dir_path)
    logging.getLogger('log_init').info(f'logger({name}, {log_dir_path})')
    return logging.getLogger(name=name)

if __name__ == '__main__':
    log = logger('potato', None)
    log.warning("warning to stdout")
    initialize('./')
    log.warning("warning to stdout and ./ file")
    initialize()
    log.warning("warning to stdout, ./ file, and default file")
