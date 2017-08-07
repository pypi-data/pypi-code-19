"""Various tools for working with objects and classes in Python"""

from objecttools.cached_property import *
from objecttools.singletons import *
from objecttools.object_proxy import *
from objecttools.serializable import *

from objecttools import cached_property, singletons, object_proxy, serializable

__all__ = ['cached_property', 'singletons', 'object_proxy', 'serializable', 'cmp']

__all__.extend(cached_property.__all__)
__all__.extend(singletons.__all__)
__all__.extend(object_proxy.__all__)
__all__.extend(serializable.__all__)

__all__ = tuple(__all__)

__author__ = 'Mital Ashok'
__credits__ = ['Mital Ashok']
__license__ = 'MIT'
__version__ = '1.0.0'
__maintainer__ = 'Mital Ashok'
__author_email__ = __email__ = 'mital.vaja@googlemail.com'
__status__ = 'Production'

try:
    from __builtin__ import cmp
except ImportError:
    def _no_cmp(a, b):
        return NotImplemented

    def cmp(x, y):
        """Return -1 if x < y, 0 if x == y, +1 if x > y."""
        type_x = type(x)
        try:
            cmp = object.__getattribute__(type_x, '__cmp__')
        except AttributeError:
            cmp = _no_cmp
        cmp = cmp(x, y)
        if cmp is not NotImplemented:
            if cmp == 0:
                return 0
            if cmp < 0:
                return -1
            if cmp > 0:
                return 1
        type_y = type(y)
        try:
            cmp = object.__getattribute__(type_y, '__cmp__')
        except AttributeError:
            cmp = _no_cmp
        cmp = cmp(y, x)
        if cmp is not NotImplemented:
            if cmp == 0:
                return 0
            if cmp < 0:
                return 1
            if cmp > 0:
                return -1
        gt = x > y
        lt = x < y
        eq = x == y
        if gt and not lt and not eq:
            return 1
        if lt and not gt and not eq:
            return -1
        if eq and not gt and not lt:
            return 0
        if isinstance(x, (set, frozenset)):
            raise TypeError('cannot compare sets using cmp()')
        if type_x is type_y:
            raise TypeError('Cannot compare {} objects with cmp()'.format(
                type_x.__name__
            ))
        raise TypeError(
            'cannot compare objects of types {} and {} with cmp()'.format(
                type_x.__name__, type_y.__name__
            )
        )
