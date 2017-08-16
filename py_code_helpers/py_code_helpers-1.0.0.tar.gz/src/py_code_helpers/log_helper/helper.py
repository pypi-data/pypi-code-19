import logging
import os


lname = os.getenv('LOG_HELPER.NAME', 'log_helper')
lfile = os.getenv('LOG_HELPER.FILE', '/tmp/log_helper.log')

# root logger
logger = logging.getLogger(lname)
logger.setLevel(logging.INFO)
fh = logging.FileHandler(lfile)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

def log(log_name=None, log_file=None):
    def decorate(function):
        def wrapper(*args, **kwargs):
            logname = lname + '.' + log_name
            logger = logging.getLogger(logname)
            if log_file:
                nfh = logging.FileHandler(log_file)
                nfh.setFormatter(formatter)
                logger.addHandler(nfh)
            function(log=logger, *args, **kwargs)
        return wrapper
    return decorate
