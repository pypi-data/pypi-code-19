import hashlib

import pylibmc


def _get_params(func, *args, **kwargs):
    """Turn an argument list into a dictionary.

    :arg function func: A function.
    :arg list *args: Positional arguments of `func`.
    :arg dict **kwargs: Keyword arguments of `func`.

    :returns dict: Dictionary representation of `args` and `kwargs`.
    """
    params = dict(zip(func.func_code.co_varnames[:len(args)], args))
    if func.func_defaults:
        params.update(dict(zip(
            func.func_code.co_varnames[-len(func.func_defaults):],
            func.func_defaults)))
    params.update(kwargs)

    return params


class Cache(object):
    """Memoisation decorator.
    """
    host = '127.0.0.1'
    port = '11211'

    def __init__(self, timeout=86400, ignore=[], key=''):
        """Constructor.

        :arg int timeout: Timeout for used entries.
        :arg list ignore: List of parameter positions and keywords to ignore.
        :arg str key: Prefix for generating the key.
        """
        self.cache = pylibmc.Client(['{}:{}'.format(self.host, self.port)])
        self.timeout = timeout
        self.ignore = ignore
        self.key = key

    def __call__(self, func):
        """Entry point.

        :arg function func: A function.
        """
        def wrapper(*args, **kwargs):
            """Wrapper function that does cache administration.
            """
            params = _get_params(func, *args, **kwargs)

            key_data = [self.key, func.__module__, func.func_name]
            for param, value in sorted(params.items()):
                key_data += [type(value).__name__, param]
                if param not in self.ignore:
                    key_data.append(value)

            key = hashlib.md5('__'.join(map(str, key_data))).hexdigest()

            result = self.cache.get(key)
            if not result:
                result = func(*args, **kwargs)
                self.cache.add(key, result, time=self.timeout)

            return result

        return wrapper

    def flush(self):
        self.cache.flush_all()
