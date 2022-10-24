import logging
import sys

root_log = logging.getLogger()
root_log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger(name=__file__)
log.addHandler(handler)
log.debug("debug")
log.info("info")
log.warning("warning")
log.error("error")
