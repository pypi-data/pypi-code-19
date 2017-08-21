
try:
    from collections import OrderedDict as odict # from Python 2.7
except ImportError:
    from .od_backport import OrderedDict as odict



class naodict(odict):
    """
    very basic attribute access for ordered dict
    names that collide with predefined names
    could not be accesed in attribute style
    """

    def __getattr__(self, key):
        if key in self:
            return self[key]
        
        return super().__getattr__(key)


    def __setattr__(self, key, value):
        if not key.startswith('_'):
            self[key] = value
        else:
            super().__setattr__(key, value)


class nao():
    """
    if you shadow important methods with __getattribute__
    like `items` then a lot of functionality that
    relies on that might not work (e.g. pprint)

    if __getattribute__ is used then it should
    not inherit from  dict or odict but create
    a new type with a hidden dictionary and
    no standard methods...
    """

    def __init__(self):
        self._dict = odict()


    def __getattribute__(self, key):
        if not key.startswith('_') and key in self._dict:
            return self._dict[key]
        
        return super().__getattribute__(key)


    def __setattr__(self, key, value):
        if not key.startswith('_'):
            self._dict[key] = value
        else:
            super().__setattr__(key, value)


    def __repr__(self):

        return self._dict.__repr__()

