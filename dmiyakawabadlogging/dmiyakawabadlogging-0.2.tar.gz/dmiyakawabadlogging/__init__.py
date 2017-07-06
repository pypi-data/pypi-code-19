import logging
import time

logger = logging.getLogger()

def mygoodfunction():
    if logger.getEffectiveLevel() < logging.INFO:
        logging.debug('Start very timeconsuming debug setup!!')
        time.sleep(2)
        logging.debug('Yahoo!!!')
        time.sleep(2)
        logging.debug('Google!!!')
        time.sleep(2)
    return 'Good Value'
