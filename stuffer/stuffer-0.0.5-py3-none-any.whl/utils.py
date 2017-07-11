"""Unsorted utility classes and routines."""


def natural_repr(obj):
    if isinstance(obj, list):
        return repr(list(map(natural_repr, obj)))
    if isinstance(obj, tuple):
        return repr(tuple(map(natural_repr, obj)))
    if isinstance(obj, dict):
        return repr(dict([map(natural_repr, kv) for kv in obj.items()]))
    return repr(obj)


def natural_object_repr(obj):
    return "{}({})".format(obj.__class__.__name__, ". ".join(
        ["{}={}".format(member, natural_repr(getattr(obj, member))) for member in dir(obj)
         if member[0] != '_' and not callable(getattr(obj, member))]))


class NaturalReprMixin(object):
    def __repr__(self):
        return natural_object_repr(self)


def str_split(cmd):
    if isinstance(cmd, str):
        return cmd.split()
    return cmd


class DeferStr(object):
    def __init__(self, supplier):
        self.supplier = supplier

    def __str__(self):
        return str(self.supplier())
