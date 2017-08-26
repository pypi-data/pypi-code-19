from functools import partial, wraps
from inspect import getfullargspec

# Modified version of fn.py decorator to support type annotations
def curried(func):
    @wraps(func)
    def _curried(*args, **kwargs):
        f = func
        count = 0
        while isinstance(f, partial):
            if f.args:
                count += len(f.args)
            f = f.func

        spec = getfullargspec(f)

        if count == len(spec.args) - len(args):
            return func(*args, **kwargs)

        return curried(partial(func, *args, **kwargs))
    return _curried
