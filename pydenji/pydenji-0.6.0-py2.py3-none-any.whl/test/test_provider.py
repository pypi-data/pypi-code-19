#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase

from pydenji.config.provider import provide_all_singletons, prototype, singleton, dontconfigure, provider
from pydenji.config.provider import is_object_factory, is_eager, _CONFIGURED_OBJECT_FACTORY

class TestConfig(TestCase):
    def test_config_configures_undecorated_public_methods(self):
        config_recorder = []
        class Simple(object):
            def public(self):
                pass
        self.conf = provide_all_singletons(Simple, config_recorder.append)
        self.assert_(Simple.public in config_recorder, "public was not configured.")

    def test_config_doesnt_configure_private_methods(self):
        class Simple(object):
            def _private(self):
                pass
        config_recorder = []
        self.conf = provide_all_singletons(Simple, config_recorder.append)
        self.assert_(not config_recorder)

    def test_config_doesnt_configure_dontconfigure_methods(self):
        class Simple(object):
            @dontconfigure
            def public(self):
                pass
        config_recorder = []
        self.conf = provide_all_singletons(Simple, config_recorder.append)
        self.assert_(not config_recorder)

    def test_config_doesnt_reconfigure_already_configured_object(self):
        class Simple(object):
            
            def already_configured(self):
                pass
            setattr(already_configured, _CONFIGURED_OBJECT_FACTORY, True)

        config_recorder = []
        self.conf = provide_all_singletons(Simple, config_recorder.append)
        self.assert_(not config_recorder)

    def test_prototype_factory_works_without_parameters(self):
        class Prototypal(object):
            @provider(scope=prototype)
            def factory(self):
                return 1

        conf = Prototypal()
        conf.factory()

    def test_lazy_factory_works_without_parameters(self):
        class Lazy(object):
            @provider(scope=prototype, lazy_init=True)
            def factory(self):
                return 1

        conf = Lazy()
        conf.factory()


class TestScopeDecorators(TestCase):
    def setUp(self):
        def iterator():
            yield 1
            yield 2
            yield 3

        self.func = iterator().send

    def test_prototype_creates_new_object_each_time(self):
        f = prototype(self.func)
        self.assertEquals([1,2,3], [f(None), f(None), f(None)])

    def test_prototype_factory_returns_factory(self):
        f = prototype.factory(self.func)()
        self.assertEquals([1,2,3], [f(None), f(None), f(None)])

    def test_prototype_factory_accepts_partial_arguments(self):
        def func(a, b):
            return a + b

        f = prototype.factory(func)(a=1)

        self.assertEquals([2, 3, 4], [f(b=1), f(b=2), f(b=3)])
        

    def test_prototype_configures_object(self):
        f = prototype(self.func)
        self.assertTrue(is_object_factory(f))

    def test_prototype_hints_for_lazy_instantiation(self):
        f = prototype(self.func)
        self.assertFalse(is_eager(f))


    def test_singleton_caches_first_returned_object(self):
        f = singleton(self.func)
        self.assertEquals([1,1,1], [f(None), f(None), f(None)])

    def test_singleton_configures_object(self):
        f = singleton(self.func)
        self.assertTrue(is_object_factory(f))

    def test_singleton_hints_for_eager_instantiation(self):
        f = singleton(self.func)
        self.assertTrue(is_eager(f))

    def test_lazy_singleton_caches_first_returned_object(self):
        f = singleton.lazy(self.func)
        self.assertEquals([1,1,1], [f(None), f(None), f(None)])

    def test_lazy_singleton_configures_object(self):
        f = singleton.lazy(self.func)
        self.assertTrue(is_object_factory(f))

    def test_lazy_singleton_hints_for_lazy_instantiation(self):
        f = singleton.lazy(self.func)
        self.assertFalse(is_eager(f))
        

