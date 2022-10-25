import logging
import sys

default_log_dir = '/opt/deadman/Web3HackerNetwork/log'

# the implementation herein is very bad and very temporary
# in the future, this will still return a named logger, but
# root logger initialization will be done through a
# configuration file
def logger(name):
    root_log = logging.getLogger()
    root_log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root_log.addHandler(handler)
    for noisy in ['boto3', 'botocore', 'urllib3']:
        logging.getLogger(noisy).setLevel(logging.WARNING)
    return logging.getLogger(name=name)
