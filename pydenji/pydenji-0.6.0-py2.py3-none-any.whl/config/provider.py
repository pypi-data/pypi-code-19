#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.

from functools import partial
from types import UnboundMethodType

from pydenji._aop.intercept import intercept
from pydenji.placeholders import Placeholder

# TODO: we might probably reduce the number of constants.
_CONFIGURED_OBJECT_FACTORY = "_pydenji__CONFIGURED_OBJECT_FACTORY"
_INSTANTIATE_EAGERLY = "_pydenji__INSTANTIATE_EAGERLY"
_SHOULD_CONFIGURE = "_pydenji__SHOULD_CONFIGURE"

def is_object_factory(obj):
    if getattr(obj, _CONFIGURED_OBJECT_FACTORY, None) is True:
        return True
    return False

def is_eager(obj):
    if getattr(obj, _INSTANTIATE_EAGERLY, None) is True:
        return True
    return False

def should_be_configured(obj):
    return getattr(obj, _SHOULD_CONFIGURE, True)

class _Maybe(object):
    def __init__(self, has_value=False, value=None):
        self.has_value = has_value
        self.value = value

def singleton(func, eager=True):
    maybevalue = _Maybe()
    def singleton_wrapped(*args, **kwargs):
        if args[1:] or kwargs:
            raise TypeError, "Singleton mustn't take any parameter. Use per-instance config instead."

        if not maybevalue.has_value:
            maybevalue.value = func(*args)
            maybevalue.has_value = True
        return maybevalue.value

    set_singleton(singleton_wrapped, eager)

    return singleton_wrapped

def set_singleton(obj, eager=True):
    setattr(obj, _INSTANTIATE_EAGERLY, eager)
    setattr(obj, _CONFIGURED_OBJECT_FACTORY, True)
    setattr(obj, _SHOULD_CONFIGURE, False)
    return obj

singleton.lazy = partial(singleton, eager=False)
singleton.default_lazy_init = False

def prototype(func, eager=False):
    if eager:
        raise ValueError, "eager instantiation makes no sense for prototype scope."
    def f(*args, **kwargs):
        return func(*args, **kwargs)
    setattr(f, _CONFIGURED_OBJECT_FACTORY, True)
    setattr(f, _INSTANTIATE_EAGERLY, False)
    setattr(f, _SHOULD_CONFIGURE, False)
    return f

prototype.default_lazy_init = True

def _prototype_factory(func):
    def f(*args, **kwargs):
        return partial(func, *args, **kwargs)
    setattr(f, _CONFIGURED_OBJECT_FACTORY, True)
    setattr(f, _INSTANTIATE_EAGERLY, False)
    setattr(f, _SHOULD_CONFIGURE, False)
    return f

prototype.factory = _prototype_factory
    
def dontconfigure(func):
    def f(*args, **kwargs):
        return func(*args, **kwargs)
    setattr(f, _SHOULD_CONFIGURE, False)
    setattr(f, _INSTANTIATE_EAGERLY, False)
    setattr(f, _CONFIGURED_OBJECT_FACTORY, False)
    return f


def _to_be_configured(clsattr, attrvalue):
    return ((not clsattr.startswith("_")) and
        isinstance(attrvalue, UnboundMethodType) and
        not is_object_factory(attrvalue) and
        should_be_configured(attrvalue))

# TODO: this function means nothing, rename it.
# TODO: make it work so that functions directly in the class
# dict are wrapped with a singleton.
def _configure_with(cls, configure_with):
    configured_dict = {}
    for clsattr in dir(cls):
        attrvalue = getattr(cls, clsattr)
        if _to_be_configured(clsattr, attrvalue):
            configured_dict[clsattr] = configure_with(attrvalue)
    return configured_dict

def provide_all_singletons(cls, configure_with=singleton, suffix=""):
    """
    Makes all public, unwrapped methods *eager singletons* by default.
    Also, after instantiation a "params" instance attribute will be set -
    it will hold a dictionary.

    Also sets required_properties init interceptor; if the class or the
    instance has got a "required_properties" attribute, after initialization
    that "resolve" required properties by settings placeholders instead.

    (this won't completely solve missing placeholder configuration, by the way).
    

    Non-public methods and already-wrapped methods will just go untouched.
    """
    configured_dict = _configure_with(cls, configure_with)
    cls_type = type(cls)
    return cls_type(cls.__name__ + suffix, (cls, ), configured_dict)


class Provider(object):
    def __init__(self, scope=singleton, lazy_init=None):
        self._scope = scope
        if lazy_init is None:
            self._eager = not scope.default_lazy_init
        else:
            self._eager = not lazy_init

    def __call__(self, func):
        return self._scope(func, self._eager)

provider = Provider








