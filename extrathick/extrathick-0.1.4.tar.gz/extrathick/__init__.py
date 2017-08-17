from steov import Anon

def anonify (obj):
    if isinstance(obj, dict):
        return Anon({k: anonify(v) for k, v in obj.items()})
    if isinstance(obj, (list, set, tuple)):
        return type(obj)(map(anonify, obj))
    return obj

def unanonify (obj):
    if isinstance(obj, Anon):
        obj = vars(Anon)
    if isinstance(obj, dict):
        return {k: unanonify(v) for k, v in obj.items()}
    if isinstance(obj, (list, set, tuple)):
        return type(obj)(map(unanonify, obj))
    return obj

# TODO json defaults for:
# * datetime
# * uuid
# * decimal

# TODO standardized way of serializing/deserializing UTC dates to strings

_stat_attrs = [
    "mode",
    "ino",
    "dev",
    "nlink",
    "uid",
    "gid",
    "size",
    "atime",
    "mtime",
    "ctime",
]

def anonstat (st):
    return Anon({attr: getattr(st, "st_"+attr) for attr in _stat_attrs})
