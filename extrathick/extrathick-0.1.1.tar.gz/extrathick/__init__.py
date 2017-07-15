from steov import Anon

def anonify (obj):
    if isinstance(obj, dict):
        return Anon({k: anonify(v) for k, v in obj.items()})
    if isinstance(obj, (list, set, tuple)):
        return type(obj)(map(anonify, obj))
    return obj

def unanonify (obj):
    if isinstance(obj, Anon):
        return {k: unanonify(v) for k, v in vars(obj)}
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
