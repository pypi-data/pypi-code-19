import functools
import time
import daiquiri

logger = daiquiri.getLogger(__name__)


def timed(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        start_time = time.time()
        func_return = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logger.info(f'Completed in {round(elapsed_time, 2)}s')
        return func_return
    return wrapped
