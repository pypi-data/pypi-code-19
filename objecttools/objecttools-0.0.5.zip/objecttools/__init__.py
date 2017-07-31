"""Various tools for working with objects and classes in Python"""

from objecttools import cached_property, singletons, object_proxy

from objecttools.cached_property import *
from objecttools.singletons import *
from objecttools.object_proxy import *

__all__ = ['cached_property', 'singletons', 'cmp']

__all__.extend(cached_property.__all__)
__all__.extend(singletons.__all__)
__all__.extend(object_proxy.__all__)

__all__ = tuple(__all__)

__author__ = 'Mital Ashok'
__credits__ = ['Mital Ashok']
__license__ = 'MIT'
__version__ = '0.0.5'
__maintainer__ = 'Mital Ashok'
__author_email__ = __email__ = 'mital.vaja@googlemail.com'
__status__ = 'Development'

try:
    from __builtin__ import cmp
except ImportError:
    def cmp(x, y):
        """Return -1 if x < y, 0 if x == y, +1 if x > y."""
        try:
            cmp = object.__getattribute__(type(x), '__cmp__')(x, y)
        except AttributeError:
            cmp = NotImplemented
        if cmp is not NotImplemented:
            if cmp == 0:
                return 0
            if cmp < 0:
                return -1
            if cmp > 0:
                return 1
        try:
            cmp = object.__getattribute__(type(y), '__cmp__')(y, x)
        except AttributeError:
            cmp = NotImplemented
        if cmp is not NotImplemented:
            if cmp == 0:
                return 0
            if cmp < 0:
                return 1
            if cmp > 0:
                return -1
        if isinstance(x, (set, frozenset)):
            gt = x > y
            lt = x < y
            eq = x == y
            if gt:
                return 1
            if lt:
                return -1
            if eq:
                return 0
            raise TypeError('cannot compare sets using cmp()')
        return (x > y) - (x < y)
