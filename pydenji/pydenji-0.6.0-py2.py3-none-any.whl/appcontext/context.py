#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.
from random import choice

from pydenji.config.provider import is_object_factory, is_eager
from pydenji.appcontext.aware import AppContextAware
from pydenji.config.pythonconfig import Configuration
from pydenji.config.composite import CompositeConfig



class UnknownProviderException(Exception):
    pass

class AlreadyRegistered(Exception):
    pass

class AppContext(object):
    def __init__(self):
        self._names_providers = {}
        self._anon_index = 1

    def register(self, name, provider):
        # TODO: limit bean names.
        if name in self._names_providers:
            raise AlreadyRegistered, "'%s' was already registered!" % name
        self._names_providers[name] = provider

    # we'll do this right now, in the future we might try with a ducktype-based
    # overloading.
    def register_anonymous(self, provider):
        self._add_anonymous_provider(provider)

    def _add_anonymous_provider(self, provider):
        self.register("_ANON_%s" % self._anon_index, provider)
        self._anon_index += 1

    def __contains__(self, key):
        return key in self._names_providers

    def __iter__(self):
        return [key for key in self._names_providers.iterkeys() if not key.startswith("_ANON")]

    def provide(self, name, *args, **kwargs):
        try:
            provider = self._names_providers[name]
        except KeyError:
            raise UnknownProviderException, "No provider was configured for '%s'" % name
        return self._get_instance(provider, *args, **kwargs)
    
    def start(self):
        for provider in self._names_providers.values():
            if is_eager(provider):
                self._get_instance(provider)

    def _get_instance(self, factory, *args, **kwargs):
        # this way the set_app_context() method will be called multiple times,
        # even though the object is a singleton. While it should make no harm,
        # we should think about it, might it do any harm?
        obj = factory(*args, **kwargs)
        if isinstance(obj, AppContextAware):
            obj.set_app_context(self)
        if isinstance(obj, Configuration):
            self._register_config_providers(obj)
        return obj

    def _register_config_providers(self, config):
        for name, provider in config.get_public_providers().items():
            # this can happen if a config is requested multiple times,
            # but what happens if such name was initially registered by
            # somebody else?
            # TODO: reconsider the issue of colliding names.
            try:
                self.register(name, provider)
            except AlreadyRegistered:
                pass







