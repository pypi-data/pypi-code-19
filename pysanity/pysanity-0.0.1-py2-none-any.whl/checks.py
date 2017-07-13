import inspect
import functools


def _obj_check(fn):
    @functools.wraps(fn)
    def wrapper(name, adapted_name, obj):
        return fn(obj)


@_obj_check
def obj_is_function_or_method(name, adapted_name, obj):
    return inspect.isfunction(obj) or inspect.ismethod(obj)
