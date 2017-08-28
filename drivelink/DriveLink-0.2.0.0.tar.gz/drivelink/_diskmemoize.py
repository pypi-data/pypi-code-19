import copy
from os.path import join, expanduser

from drivelink import Dict


class _Cached:
    "This will shine the most with recursive functions. But the recursion has to call the cached function, not the function itself."
    f = None
    c = None

    def __init__(self, function, file_basename=None, size_limit=1024, max_pages=16, file_location=join(expanduser("~"), ".DriveLink")):
        for n in list(n for n in set(dir(function)) - set(dir(self)) if n != '__class__'):
            setattr(self, n, getattr(function, n))
        if file_basename is None:
            file_basename = function.__name__
        self.f = function
        self.c = Dict(file_basename, size_limit, max_pages, file_location)

    def __call__(self, *args, **kwargs):
        i = str(args) + str(kwargs)
        if i in self.c:
            return copy.deepcopy(self.c[i])
        else:
            t = self.f(*args, **kwargs)
            self.c[i] = copy.deepcopy(t)
            return t


def cached(file_basename=None, size_limit=1024, max_pages=16, file_location=join(expanduser("~"), ".DriveLink")):
    '''
    A decorator that creates a simplistic cached function with minimal overhead.

    This provides very simplistic and quick cache. The values are saved to a drivelink.Dict
    and will be reloaded on program restarting.
    '''
    def decorator(f):
        return _Cached(f, file_basename, size_limit, max_pages, file_location)
    return decorator
