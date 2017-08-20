"""log object instantiation of (almost) all python classes

Import the module using ``from mtoolbox import instancelog``

Note:
    You have to run ``enable()`` BEFORE importing
    the module, which has classes you would like to log.
    The reason for this is, that the name ``object`` from the
    ``__builtin__`` namespace has to point to the object class overwrite
    of the instancelog module, when a new class is defined. For the same
    reason builtin objects will never be logged.

Example:

In this example ``MyClass1`` objects will not be logged, while
``MyClass2`` objects will be logged:

>>> from . import instancelog
>>> class MyClass1(object):
...     def __repr__(self):
...         return 'MyClass1 object'
>>> instancelog.enable()
>>> class MyClass2(object):
...     def __repr__(self):
...         return 'MyClass2 object'
>>> objlist = []
>>> def my_callback(obj, cls, args, kwargs):
...   objlist.append(obj)
>>> instancelog.callbacks.append(my_callback)
>>> obj1 = MyClass1()
>>> obj2 = MyClass2()
>>> print(objlist)
[MyClass2 object]
"""

import sys

if sys.version_info[0] == 2:
    import __builtin__ as builtins
else:
    import builtins

_object = object
callbacks = []

class Object(object):
    """Class to replace (builtin) object"""
    def __new__(cls, *args, **kwargs):
        obj = _object.__new__(cls, *args, **kwargs)
        for func in callbacks:
            func(obj, cls, args, kwargs)
        return obj

def enable():
    """Enable the logging of objects."""
    builtins.object = Object

def disable():
    """Disable the logging of objects."""
    builtins.object = _object

if __name__ == '__main__':
    import doctest
    doctest.testmod()
