#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni

from pydenji.appcontext.aware import AppContextAware
from pydenji.config.provider import provide_all_singletons
from pydenji.config.provider import singleton


def _set_app_context(self, context):
    self._pydenji__app_context = context

def _getattr(self, attr):
    # THIS IS BAD!
    try:
        return lambda *args, **kwargs: self._pydenji__app_context.provide(attr, *args, **kwargs)
    except:
        # TODO: better error interception! just intercept what we
        # need to handle.
        raise KeyError, "'%s' object has no attribute '%s'" % (self, attr)

def ContextConfiguration(cls, configure_with=singleton, suffix=""):
    """
    Just like Configuration, but any unfound factory will be looked up in the app context.
    """
    
    ConfigClass = provide_all_singletons(cls, configure_with, suffix)
    # it might be appcontext aware but we
    # could not detect it without ABCs...
    # TODO: think about that.
    if getattr(ConfigClass, "set_app_context", None):
        # just return it, it's already got whatever it needs. (maybe?)
        # TODO: let's think if this can do any harm.
        return ConfigClass

    configured_dict = {}

    configured_dict["set_app_context"] = _set_app_context
    configured_dict["_pydenji__app_context"] = None
    configured_dict["__getattr__"] = _getattr

    cls_type = type(cls)
    return cls_type(cls.__name__ + suffix, (ConfigClass, ), configured_dict)
