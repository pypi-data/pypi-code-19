"""Descriptors that cache values from a getter, like a property"""

import threading
import types

from objecttools.singletons import Singleton

__all__ = ('CachedProperty', 'ThreadedCachedProperty')

_Missing = Singleton.create('_Missing', object_name='_missing')
_missing = _Missing()

_NO_DICT_ERROR = (
    'Instance "{instance!r}" of type "{type!r}" has no __dict__ attribute. '
    'If it has a __slots__ attribute, please add `__dict__` to the slots.'
)

_NO_NAME_ERROR = (
    'Cannot get name of attribute to assign to for instance "{instance!r}" of '
    'type "{type!r}".'
)

_FUNC_DOC = '__doc__' if hasattr(types.FunctionType, '__doc__') else 'func_doc'
_FUNC_NAME = '__name__' if hasattr(types.FunctionType, '__name__') else 'func_name'


def _get_dict(obj):
    __dict__ = getattr(obj, '__dict__', _missing)
    if __dict__ is _missing:
        try:
            obj.__dict__ = {}
        except AttributeError:
            pass
        __dict__ = getattr(obj, '__dict__', _missing)
        if __dict__ is _missing:
            raise AttributeError(
                _NO_DICT_ERROR.format(instance=obj, type=type(obj))
            )
    return __dict__


class CachedProperty(object):
    """A property that caches its return value"""
    __slots__ = ('_name', '_getter', '_setter', '_deleter', '_doc', '__weakref__')

    def __init__(self, fget=None, can_set=False, can_del=False, doc=None, name=None):
        if doc is None:
            doc = getattr(fget, _FUNC_DOC, None)
        if name is None:
            name = getattr(fget, _FUNC_NAME, None)
        self._getter = fget
        self._setter = bool(can_set)
        self._deleter = bool(can_del)
        if type(name) is str or name is None:
            self._name = name
        else:
            raise TypeError('"name" must be a str or None')
        if type(doc) is str or doc is None:
            self._doc = doc
        else:
            raise TypeError('"__doc__" must be a str or None')

    @property
    def name(self):
        """The name of the attribute that this descriptor is a property for"""
        return self._name

    @name.setter
    def name(self, value):
        if type(value) is str or value is None:
            self._name = value
        else:
            raise TypeError('"name" must be a str or None')

    @name.deleter
    def name(self):
        self._name = None

    @property
    def __doc__(self):
        return self._doc

    @__doc__.setter
    def __doc__(self, value):
        if type(value) is str or value is None:
            self._doc = value
        else:
            raise TypeError('"__doc__" must be a str or None')

    @__doc__.deleter
    def __doc__(self):
        self._doc = None

    def getter(self, fget):
        """
        Change the getter for this descriptor to use to get the value

        :param fget: Function to call with an object as its only argument
        :type fget: Callable[[Any], Any]
        :return: self, so this can be used as a decorator like a `property`
        :rtype: CachedProperty
        """
        if getattr(self, '__doc__', None) is None:
            self.__doc__ = getattr(fget, _FUNC_DOC, None)
        if self.name is None:
            self.name = getattr(fget, _FUNC_NAME, None)
        self._getter = fget
        return self

    def setter(self, can_set=None):
        """
        Like `CachedProp.deleter` is for `CachedProp.can_delete`, but for `can_set`

        :param can_set: boolean to change to it, and None to toggle
        :type can_set: Optional[bool]
        :return: self, so this can be used as a decorator like a `property`
        :rtype: CachedProperty
        """
        if can_set is None:
            self._setter = not self._setter
        else:
            self._setter = bool(can_set)
        # For use as decorator
        return self

    @property
    def can_set(self):
        """Whether this descriptor supports setting the value"""
        return self._setter

    @can_set.setter
    def can_set(self, value):
        self.setter(value)

    @can_set.deleter
    def can_set(self):
        self._setter = False

    def deleter(self, can_delete=None):
        """
        Change if this descriptor's can be invalidated through `del obj.attr`.

        `cached_prop.deleter(True)` and::

            @cached_prop.deleter
            def cached_prop(self):
                pass

        are equivalent to `cached_prop.can_delete = True`.

        :param can_delete: boolean to change to it, and None to toggle
        :type can_delete: Optional[bool]
        :return: self, so this can be used as a decorator like a `property`
        :rtype: CachedProperty
        """
        if can_delete is None:
            self._deleter = not self._deleter
        else:
            self._deleter = bool(can_delete)
        # For use as decorator
        return self

    @property
    def can_delete(self):
        """Whether this descriptor supports invalidation through `del`"""
        return self._deleter

    @can_delete.setter
    def can_delete(self, value):
        self.deleter(value)

    @can_delete.deleter
    def can_delete(self):
        self._deleter = False

    def __get__(self, instance=None, owner=None):
        if instance is None:
            return self
        if self._getter is None:
            raise AttributeError('unreadable attribute')
        if self.name is not None:
            __dict__ = _get_dict(instance)
            cached = __dict__.get(self.name, _missing)
            if cached is _missing:
                cached = __dict__[self.name] = self._getter(instance)
            return cached
        else:
            raise ValueError(_NO_NAME_ERROR.format(instance=instance, type=type(instance)))

    def __set__(self, instance=None, value=None):
        if instance is None:
            return self
        if not self.can_set:
            raise AttributeError('can\'t set attribute')
        if self.name is not None:
            _get_dict(instance)[self.name] = value
        else:
            raise ValueError(_NO_NAME_ERROR.format(instance=instance, type=type(instance)))

    def __delete__(self, instance=None):
        if instance is None:
            return self
        if not self.can_delete:
            raise AttributeError('can\'t delete attribute')
        if self.name is not None:
            _get_dict(instance).pop(self.name, None)
        else:
            raise ValueError(_NO_NAME_ERROR.format(instance=instance, type=type(instance)))

    def is_cached(self, instance):
        """
        Return whether a property named `name` has been cached.

        To check if CachedProperty `x` of object `o` is cached, use::

            type(o).x.is_cached(o)

        Or if you know that `isinstance(o, T)` (and `T.x is type(o).x`)

            T.x.is_cached(o)

        :param instance: An object with a cached property
        :type instance: Any
        :param name: The name of the property to check for the cache of
        :type name: str
        :return: `True` if the property is cached. `False` otherwise.
        :rtype: bool
        """
        return self.name in _get_dict(instance)


class ThreadedCachedProperty(CachedProperty):
    """Thread-safe version of CachedProperty"""
    __slots__ = ('_name', '_getter', '_setter', '_deleter', 'lock', '_doc')

    def __init__(self, fget=None, can_set=False, can_del=False,
                 doc=None, name=None, lock=threading.RLock):
        if callable(lock):
            lock = lock()
        self.lock = lock

        super(ThreadedCachedProperty, self).__init__(fget, can_set, can_del, doc, name)

    def getter(self, fget):
        with self.lock:
            return super(ThreadedCachedProperty, self).getter(fget)

    def setter(self, can_set=None):
        with self.lock:
            return super(ThreadedCachedProperty, self).setter(can_set)

    def deleter(self, can_delete=None):
        with self.lock:
            return super(ThreadedCachedProperty, self).deleter(can_delete)

    def __get__(self, instance=None, owner=None):
        with self.lock:
            return super(ThreadedCachedProperty, self).__get__(instance, owner)

    def __set__(self, instance=None, value=None):
        with self.lock:
            return super(ThreadedCachedProperty, self).__set__(instance, value)

    def __delete__(self, instance=None):
        with self.lock:
            return super(ThreadedCachedProperty, self).__delete__(instance)

    def is_cached(self, instance):
        with self.lock:
            return super(ThreadedCachedProperty, self).is_cached(instance)

    # Doesn't work otherwise, as overridden with docstring
    __doc__ = CachedProperty.__doc__
