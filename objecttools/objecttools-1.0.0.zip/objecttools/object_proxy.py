"""Define a proxy object for a Python objects, supporting the same dunder methods"""

import sys
from operator import (
    __abs__, __add__, __and__, __contains__, __delitem__,
    __eq__, __ge__, __getitem__, __gt__, __iadd__, __iand__,
    __ilshift__, __imod__, __imul__, __invert__, __ior__, __ipow__,
    __irshift__, __isub__, __ixor__, __le__, __lshift__, __lt__,
    __mod__, __mul__, __ne__, __neg__, __or__, __pos__, __pow__,
    __rshift__, __setitem__, __sub__, __xor__
)

from objecttools.singletons import Singleton

__all__ = ('ObjectProxy', 'get_wrapped_object')


_NotGiven = Singleton.create('_NotGiven', object_name='_not_given')
_not_given = _NotGiven()

try:
    from operator import __floordiv__, __ifloordiv__
except ImportError:
    __floordiv__ = __ifloordiv__ = None

try:
    from operator import __truediv__, __itruediv__
except ImportError:
    __truediv__ = __itruediv__ = None

try:
    from operator import __div__, __idiv__
except ImportError:
    __div__ = __idiv__ = None

try:
    from operator import __repeat__, __irepeat__
except ImportError:
    __repeat__ = __irepeat__ = None

try:
    __cmp__ = cmp
    __rcmp__ = sys.version_info < (2, 1)
except NameError:
    __cmp__ = __rcmp__ = None

try:
    bool.__nonzero__
    __nonzero__ = bool
except AttributeError:
    __nonzero__ = None

try:
    bool.__bool__
    __bool__ = bool
except AttributeError:
    __bool__ = None

try:
    __unicode__ = unicode
    __bytes__ = None
except NameError:
    __unicode__ = None
    __bytes__ = bytes

__reversed__ = __instancecheck__ = __subclasscheck__ = sys.version_info >= (2, 6)

try:
    from operator import __getslice__, __setslice__, __delslice__
except ImportError:
    __getslice__ = __setslice__ = __delslice__ = None

try:
    from operator import __index__
except ImportError:
    __index__ = None

try:
    __long__ = long
except NameError:
    __long__ = None

try:
    __coerce__ = coerce
except NameError:
    __coerce__ = None

__enter__ = __exit__ = sys.version_info >= (2, 5)

try:
    from operator import __matmul__, __imatmul__
except ImportError:
    __matmul__ = __imatmul__ = None

try:
    from operator import length_hint as __length_hint__
except ImportError:
    __length_hint__ = None

__missing__ = sys.version_info >= (3,)

__await__ = sys.version_info >= (3, 5)

try:
    from types import InstanceType
except ImportError:
    InstanceType = object()  # To be unique


def get_wrapped_object(obj):
    """
    If an `obj` is an `ObjectProxy` instance, return the object wrapped by it.
    Otherwise, return the object.

    :param obj: The object to possibly unwrap.
    :return: Not an `ObjectProxy`.
    """
    if isinstance(obj, ObjectProxy):
        return object.__getattribute__(obj, '_obj')
    return obj


def _invoke(self, attr, *args):
    obj = get_wrapped_object(self)
    cls = type(obj)
    if cls is InstanceType:
        return getattr(obj, attr)(*map(get_wrapped_object, args))
    try:
        method = object.__getattribute__(cls, attr)
    except AttributeError:
        return NotImplemented
    return method(obj, *map(get_wrapped_object, args))


class ObjectProxy(object):
    """
    A wrapper around an object that acts as if it is the object
    in most situations.

    Useful for subclassing, and checking if dunder methods exist in the current
    Python version.
    """
    def __init__(self, obj):
        object.__setattr__(self, '_obj', get_wrapped_object(obj))

    def __del__(self):
        """del self"""
        return _invoke(self, '__del__')

    def __repr__(self):
        """
        repr(self)

        NOTE:
             `repr(ObjectProxy(obj))` is not equivalent to `repr(obj)`.
        """
        return '{0.__name__}({1!r})'.format(
            type(self), get_wrapped_object(self)
        )

    def __str__(self):
        """str(self)"""
        return str(get_wrapped_object(self))

    def __lt__(self, other):
        """self < other"""
        return __lt__(get_wrapped_object(self), get_wrapped_object(other))

    def __le__(self, other):
        """self <= other"""
        return __le__(get_wrapped_object(self), get_wrapped_object(other))

    def __eq__(self, other):
        """self == other"""
        return __eq__(get_wrapped_object(self), get_wrapped_object(other))

    def __ne__(self, other):
        """self != other"""
        return __ne__(get_wrapped_object(self), get_wrapped_object(other))

    def __gt__(self, other):
        """self > other"""
        return __gt__(get_wrapped_object(self), get_wrapped_object(other))

    def __ge__(self, other):
        """self >= other"""
        return __ge__(get_wrapped_object(self), get_wrapped_object(other))

    if __cmp__:
        def __cmp__(self, other):
            """cmp(self, other)"""
            return __cmp__(get_wrapped_object(self), get_wrapped_object(other))

    if __rcmp__:
        def __rcmp__(self, other):
            """cmp(other, self)"""
            return __cmp__(other, get_wrapped_object(self))

    def __hash__(self):
        """
        hash(self)

        NOTE:
             All ObjectProxy instances have
             `isinstance(self, collections.Hashable) == True` as `__hash__`
             is not set to `None`. It will still raise a `TypeError` on
             unhashable objects (e.g. `hash(ObjectProxy([]))` fails)
        """
        return hash(get_wrapped_object(self))

    if __nonzero__:
        def __nonzero__(self):
            """self != 0"""
            return __nonzero__(get_wrapped_object(self))

    if __bool__:
        def __bool__(self):
            """bool(self)"""
            return __bool__(get_wrapped_object(self))

    if __unicode__:
        def __unicode__(self):
            """unicode(self)"""
            return __unicode__(get_wrapped_object(self))

    def __getattr__(self, name):
        """If `self.__getattribute__(name) fails, `self.__getattr__(name)` is returned"""
        return _invoke(self, '__getattr__', name)

    def __setattr__(self, name, value):
        """self.`name` = value"""
        return setattr(get_wrapped_object(self), get_wrapped_object(name), get_wrapped_object(value))

    def __delattr__(self, name):
        """del self.`name`"""
        return delattr(get_wrapped_object(self), get_wrapped_object(name))

    def __getattribute__(self, name):
        """self.`name`"""
        return _invoke(self, '__getattribute__', name)

    def __get__(self, instance, owner=_not_given):
        """descr.__get__(obj[, type]) -> value"""
        if owner is _not_given:
            return _invoke(self, '__get__', instance)
        return _invoke(self, '__get__', instance, owner)

    def __set__(self, instance, value):
        return _invoke(self, '__set__', instance, value)

    def __delete__(self, instance):
        return _invoke(self, '__delete__', instance)

    if __instancecheck__:
        def __instancecheck__(self, instance):
            """isinstance(instance, self)"""
            return isinstance(get_wrapped_object(instance), get_wrapped_object(self))

    if __subclasscheck__:
        def __subclasscheck__(self, subclass):
            """issubclass(subclass, self)"""
            return issubclass(get_wrapped_object(subclass), get_wrapped_object(self))

    def __call__(self, *args, **kwargs):
        """self(*args, **kwargs)"""
        return get_wrapped_object(self)(*args, **kwargs)

    def __len__(self):
        """len(self)"""
        return len(get_wrapped_object(self))

    def __getitem__(self, key):
        """self[key]"""
        return __getitem__(get_wrapped_object(self), get_wrapped_object(key))

    def __setitem__(self, key, value):
        """self[key] = value"""
        return __setitem__(get_wrapped_object(self), get_wrapped_object(key), get_wrapped_object(value))

    def __delitem__(self, key):
        """del self[key]"""
        return __delitem__(get_wrapped_object(self), get_wrapped_object(key))

    def __iter__(self):
        """iter(self)"""
        return iter(get_wrapped_object(self))

    if __reversed__:
        def __reversed__(self):
            """reversed(self)"""
            return reversed(get_wrapped_object(self))

    def __contains__(self, item):
        """item in self"""
        return __contains__(get_wrapped_object(self), get_wrapped_object(item))

    if __getslice__:
        def __getslice__(self, i, j):
            """self[i:j]"""
            return __getslice__(
                get_wrapped_object(self),
                get_wrapped_object(i), get_wrapped_object(j)
            )

    if __setslice__:
        def __setslice__(self, i, j, sequence):
            """self[i:j] = sequence"""
            return __setslice__(
                get_wrapped_object(self), get_wrapped_object(i),
                get_wrapped_object(j), get_wrapped_object(sequence)
            )

    if __delslice__:
        def __delslice__(self, i, j):
            """del self[i:j]"""
            return __delslice__(
                get_wrapped_object(self),
                get_wrapped_object(i), get_wrapped_object(j)
            )

    def __add__(self, other):
        """self + other"""
        return __add__(get_wrapped_object(self), get_wrapped_object(other))

    def __sub__(self, other):
        """self - other"""
        return __sub__(get_wrapped_object(self), get_wrapped_object(other))

    def __mul__(self, other):
        """self * other"""
        return __mul__(get_wrapped_object(self), get_wrapped_object(other))

    if __floordiv__:
        def __floordiv__(self, other):
            """self // other"""
            return __floordiv__(get_wrapped_object(self), get_wrapped_object(other))

    def __mod__(self, other):
        """self % other"""
        return __mod__(get_wrapped_object(self), get_wrapped_object(other))

    def __divmod__(self, other):
        """divmod(self, other)"""
        return divmod(get_wrapped_object(self), get_wrapped_object(other))

    def __pow__(self, other, modulo=_not_given):
        """
        self ** other, pow(self, other)

         pow(self, other, modulo)
        """
        if modulo is _not_given:
            return __pow__(get_wrapped_object(self), get_wrapped_object(other))
        return pow(
            get_wrapped_object(self), get_wrapped_object(other),
            get_wrapped_object(modulo)
        )

    def __lshift__(self, other):
        """self << other"""
        return __lshift__(get_wrapped_object(self), get_wrapped_object(other))

    def __rshift__(self, other):
        """self >> other"""
        return __rshift__(get_wrapped_object(self), get_wrapped_object(other))

    def __and__(self, other):
        """self & other"""
        return __and__(get_wrapped_object(self), get_wrapped_object(other))

    def __xor__(self, other):
        """self ^ other"""
        return __xor__(get_wrapped_object(self), get_wrapped_object(other))

    def __or__(self, other):
        """self | other"""
        return __or__(get_wrapped_object(self), get_wrapped_object(other))

    if __div__:
        def __div__(self, other):
            """self / other"""
            return __div__(get_wrapped_object(self), get_wrapped_object(other))

    if __truediv__:
        def __truediv__(self, other):
            """self / other"""
            return __truediv__(
                get_wrapped_object(self), get_wrapped_object(other)
            )

    if __repeat__:
        def __repeat__(self, other):
            """self * other"""
            return __repeat__(
                get_wrapped_object(self), get_wrapped_object(other)
            )

    def __radd__(self, other):
        """other + self"""
        return __add__(other, get_wrapped_object(self))

    def __rsub__(self, other):
        """other - self"""
        return __sub__(other, get_wrapped_object(self))

    def __rmul__(self, other):
        """other * self"""
        return __mul__(other, get_wrapped_object(self))

    if __floordiv__:
        def __rfloordiv__(self, other):
            """other // self"""
            return __floordiv__(other, get_wrapped_object(self))

    def __rmod__(self, other):
        """other % self"""
        return __mod__(other, get_wrapped_object(self))

    def __rdivmod__(self, other):
        """divmod(other, self)"""
        return divmod(other, get_wrapped_object(self))

    def __rpow__(self, other):
        """other ** self, pow(other, self)"""
        return __pow__(other, get_wrapped_object(self))

    def __rlshift__(self, other):
        """other << self"""
        return __lshift__(other, get_wrapped_object(self))

    def __rrshift__(self, other):
        """other >> self"""
        return __rshift__(other, get_wrapped_object(self))

    def __rand__(self, other):
        """other & self"""
        return __and__(other, get_wrapped_object(self))

    def __rxor__(self, other):
        """other ^ self"""
        return __xor__(other, get_wrapped_object(self))

    def __ror__(self, other):
        """other | self"""
        return __or__(other, get_wrapped_object(self))

    if __div__:
        def __rdiv__(self, other):
            """other / self"""
            return __div__(other, get_wrapped_object(self))

    if __truediv__:
        def __rtruediv__(self, other):
            """other // self"""
            return __truediv__(other, get_wrapped_object(self))

    if __repeat__:
        def __rrepeat__(self, other):
            """other * self"""
            return __repeat__(
                get_wrapped_object(other), get_wrapped_object(self)
            )

    def __iadd__(self, other):
        """self += other"""
        return __iadd__(get_wrapped_object(self), get_wrapped_object(other))

    def __isub__(self, other):
        """self -= other"""
        return __isub__(get_wrapped_object(self), get_wrapped_object(other))

    def __imul__(self, other):
        """self *= other"""
        return __imul__(get_wrapped_object(self), get_wrapped_object(other))

    if __ifloordiv__:
        def __ifloordiv__(self, other):
            """self //= other"""
            return __ifloordiv__(
                get_wrapped_object(self), get_wrapped_object(other)
            )

    def __imod__(self, other):
        """self %= other"""
        return __imod__(get_wrapped_object(self), get_wrapped_object(other))

    def __ipow__(self, other, modulo=_not_given):
        """self **= other"""
        if modulo is _not_given:
            return __ipow__(get_wrapped_object(self), get_wrapped_object(other))
        return _invoke(self, '__ipow__', other, modulo)

    def __ilshift__(self, other):
        """self <<= other"""
        return __ilshift__(get_wrapped_object(self), get_wrapped_object(other))

    def __irshift__(self, other):
        """self >>= other"""
        return __irshift__(get_wrapped_object(self), get_wrapped_object(other))

    def __iand__(self, other):
        """self &= other"""
        return __iand__(get_wrapped_object(self), get_wrapped_object(other))

    def __ixor__(self, other):
        """self ^= other"""
        return __ixor__(get_wrapped_object(self), get_wrapped_object(other))

    def __ior__(self, other):
        """self |= other"""
        return __ior__(get_wrapped_object(self), get_wrapped_object(other))

    if __idiv__:
        def __idiv__(self, other):
            """self /= other"""
            return __idiv__(
                get_wrapped_object(self), get_wrapped_object(other)
            )

    if __itruediv__:
        def __itruediv__(self, other):
            """self //= other"""
            return __itruediv__(
                get_wrapped_object(self), get_wrapped_object(other)
            )

    if __irepeat__:
        def __irepeat__(self, other):
            """self *= other"""
            return __irepeat__(
                get_wrapped_object(self), get_wrapped_object(other)
            )

    def __neg__(self):
        """-self"""
        return __neg__(get_wrapped_object(self))

    def __pos__(self):
        """+self"""
        return __pos__(get_wrapped_object(self))

    def __abs__(self):
        """abs(self)"""
        return __abs__(get_wrapped_object(self))

    def __invert__(self):
        """~self"""
        return __invert__(get_wrapped_object(self))

    def __complex__(self):
        """complex(self)"""
        return complex(get_wrapped_object(self))

    def __int__(self):
        """int(self)"""
        return int(get_wrapped_object(self))

    if __long__:
        def __long__(self):
            """long(self)"""
            return __long__(get_wrapped_object(self))

    def __float__(self):
        """float(self)"""
        return float(get_wrapped_object(self))

    def __oct__(self):
        """oct(self)"""
        return oct(get_wrapped_object(self))

    def __hex__(self):
        """hex(self)"""
        return hex(get_wrapped_object(self))

    if __index__:
        def __index__(self):
            """operator.index(self)"""
            return __index__(get_wrapped_object(self))

    if __coerce__:
        def __coerce__(self, other):
            """coerce(self)"""
            return __coerce__(
                get_wrapped_object(self), get_wrapped_object(other)
            )

    if __enter__:
        def __enter__(self):
            """Enter self as context manager"""
            return _invoke(self, '__enter__')

    if __exit__:
        def __exit__(self, exc_type, exc_value, traceback):
            """Exit self as context manager"""
            return _invoke(self, '__enter__', exc_type, exc_value, traceback)

    # Python 3 only methods

    if __bytes__:
        def __bytes__(self):
            """bytes(self)"""
            return bytes(get_wrapped_object(self))

    if __length_hint__:
        def __length_hint__(self):
            """operator.length_hint(self)"""
            return __length_hint__(get_wrapped_object(self))

    if __missing__:
        def __missing__(self, key):
            """Called for dict subclasses for `d[key]` when `key not in d`."""
            return _invoke(self, '__missing__', key)

    if __matmul__:
        def __matmul__(self, other):
            """self @ other"""
            return __matmul__(
                get_wrapped_object(self), get_wrapped_object(other)
            )

        def __rmatmul__(self, other):
            """other @ self"""
            return __matmul__(
                get_wrapped_object(other), get_wrapped_object(self)
            )

    if __imatmul__:
        def __imatmul__(self, other):
            """self @= other"""
            return __imatmul__(
                get_wrapped_object(self), get_wrapped_object(other)
            )

    if __await__:
        def __await__(self):
            return _invoke(self, '__await__')

        def __aiter__(self):
            return _invoke(self, '__aiter__')

        def __anext__(self):
            return _invoke(self, '__anext__')

        def __aenter__(self):
            return _invoke(self, '__aenter__')

        def __aexit__(self, exc_type, exc_val, traceback):
            return _invoke(self, '__aexit__', exc_type, exc_val, traceback)
