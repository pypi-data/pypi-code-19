"""
greenlets that don't print exceptions to the screen and can reraise the exception through 'join' / 'joinall'
"""

import gevent
import sys
from logging import getLogger

logger = getLogger(__name__)


class SilentGreenletExceptionWrapper(object):
    def __init__(self, exc_info):
        self.exc_info = exc_info

    def get_exc_info(self):
        return self.exc_info


def wrap_uncaught_greenlet_exceptions(func):
    def _func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseException as e:
            logger.exception("uncaught exception in greenlet")
            return SilentGreenletExceptionWrapper(sys.exc_info())
    _func.__name__ = repr(func)
    return _func


def spawn(func, *args, **kwargs):
    """ spawns a greenlet that does not print exceptions to the screen.
    if you use this function you MUST use this module's join or joinall otherwise the exception will be lost """
    return gevent.spawn(wrap_uncaught_greenlet_exceptions(func), *args, **kwargs)


def join(greenlet, timeout=None, raise_error=True):
    value = greenlet.get(block=True, timeout=timeout)
    if isinstance(value, SilentGreenletExceptionWrapper):
        if raise_error:
            raise value.get_exc_info()
        else:
            return None
    return value


def joinall(greenlets, timeout=None, raise_error=True):
    # this will not raise or print errors if the greenlets were spawned with 'spawn' from this module:
    gevent.joinall(greenlets, timeout=timeout)
    # raise errors if needed and there were any
    if raise_error:
        [join(greenlet) for greenlet in greenlets]
