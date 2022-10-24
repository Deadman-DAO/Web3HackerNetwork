import sys
import logging

clog = logging.getLogger(name=__file__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

clog.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
clog.addHandler(handler)

clog.debug('Debuggification')
clog.info('Info')
clog.warning('The building is on fire!')
clog.error('Error')
clog.critical('PANIC!')
clog.log(1234666, 'Spit this out mutha pho-kah')
clog.error(("One", 2, "three"))

try:
    pass
#    x = 1 / 0
#    raise(Exception('Not good!'))
except Exception as e:
    clog.log(666, 'Fred did bad things', e, exc_info=sys.exc_info())


def log(message):
    clog.critical(message)