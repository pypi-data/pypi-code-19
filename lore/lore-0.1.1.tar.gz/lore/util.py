import sys
import os
from contextlib import contextmanager
import logging
import re
from datetime import datetime
if sys.version_info.major == 3:
    import shutil


# Logging
# ----------------------------------
class SecretFilter(logging.Filter):
    PASSWORD_MATCH = re.compile(
        r'((secret|key|access|pass|pw).*?[=:][^\w]*)\w+',
        flags=re.IGNORECASE
    )
    URL_MATCH = re.compile(
        r'://([^:]+):([^@]+)(@.*)',
        flags=re.IGNORECASE
    )
    
    def filter(self, record):
        if record is None:
            return True
        record.msg = str(record.msg)
        record.msg = re.sub(SecretFilter.PASSWORD_MATCH, r'\1XXX', record.msg)
        record.msg = re.sub(SecretFilter.URL_MATCH, r'://XXX:XXX\3', record.msg)
        return True


env = os.environ.get('LORE_ENV', 'development')

logger = logging.getLogger(__name__)
logger.addFilter(SecretFilter())

if env == 'development':
    logger.setLevel(logging.DEBUG)
elif env == 'test':
    logger.setLevel(logging.WARN)
else:
    logger.setLevel(logging.INFO)

if len(logger.handlers) == 0:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt='%(asctime)s.%(msecs)03d %(message)s',
            datefmt='%H:%M:%S'
        )
    )
    logger.addHandler(handler)


@contextmanager
def timer(message="elapsed time:", level=logging.INFO):
    start = datetime.now()
    try:
        yield
    finally:
        logger.log(level, '%s %s' % (message, datetime.now() - start))


def which(command):
    if sys.version_info.major < 3:
        paths = os.environ['PATH'].split(os.pathsep)
        return any(
            os.access(os.path.join(path, command), os.X_OK) for path in paths
        )
    else:
        return shutil.which(command)


