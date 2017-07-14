
import ctypes
from ctypes.util import find_library


_libpq = None
# The global instance of the ctypes libpq library wrapper.  Once initialized, it is cached here
# and used by all connections.


def getlibpq(libname='pq'):
    """
    Return the libpq ctypes library.  To ensure the application is initialized, this is not
    called until the first connection is made.  To initialize earlier you can call this
    manually.
    """
    global _libpq

    if not _libpq:
        fqn = find_library(libname)
        logger.debug('libpq library = %r', fqn)
        if not fqn:
            # TODO: What is the right exception here?
            raise Exception("Cannot find libpq")
        _libpq = cdll.LoadLibrary(fqn)

    return _libpq
