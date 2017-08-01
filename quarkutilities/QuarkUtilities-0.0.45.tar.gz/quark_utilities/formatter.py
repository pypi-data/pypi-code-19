import collections
import functools
from pprint import pprint


class BaseFormatter(object):

    @classmethod
    def format(self, data, **kwargs):
        if 'log' in data:
            del data['log']
        return self.do_format(data)

    @classmethod
    def do_format(self, data):
        raise NotImplemented


def format_output(formatter_func):
    def deco(f):
        async def wrapper(*args, **kwargs):
            result = await f(*args, **kwargs)
            if isinstance(result, dict):
                result = formatter_func(result)
            elif isinstance(result, collections.Iterable) and not isinstance(result, (str, dict)):
                result = [formatter_func(_result) for _result in result]
            return result
        return wrapper
    return deco



