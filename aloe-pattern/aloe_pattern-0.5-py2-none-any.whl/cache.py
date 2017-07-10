""" Singleton write cache w/ grouped sorting used to prevent clobbering. """

from collections import defaultdict

_cache = defaultdict(lambda: [[] for x in xrange(2)])

def clear():
    _cache.clear()

def cached(path):
    return path in _cache

def get(path):
    return [i for s in _cache[path] for i in s]

def dump():
    for path in _cache.keys():
        yield (path, get(path))

def delete(path, value):
    for ls in _cache[path]:
        if value in ls:
            ls.remove(value)

def store(path, listordinal, value):
    ls = _cache[path][listordinal]
    if value not in ls:
        ls.append(value)

