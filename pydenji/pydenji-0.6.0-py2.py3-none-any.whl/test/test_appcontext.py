#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni

from unittest import TestCase

from pydenji.appcontext.context import AppContext, UnknownProviderException, AlreadyRegistered
from pydenji.appcontext.aware import AppContextAware
from pydenji.config.provider import provider



class MockConfig(object):
    context = None

    def get_public_providers(self):
        return {"something": lambda:True}

    def set_app_context(self, context):
        self.context = context

@provider()
def mock_config_provider():
    return MockConfig()

class TestAppContext(TestCase):
    def setUp(self):
        self.appcontext = AppContext()
        self.appcontext.register("myname", lambda x,y : x*y)

    def test_provide_creates_object_from_registered_provider(self):
        self.assertEquals(6, self.appcontext.provide("myname", 3, 2))

    def test_provide_raises_exception_if_unknown_name(self):
        self.assertRaises(UnknownProviderException, self.appcontext.provide, "noname")


    def test_appcontext_is_set_on_aware_objects(self):

        class SomeObj(object):
            app_context = None
            def set_app_context(self, context):
                self.app_context = context

        self.appcontext.register("someobj", SomeObj)

        obj = self.appcontext.provide("someobj")
        self.assertTrue(self.appcontext is obj.app_context, "context wasn't injected correctly!")

    def test_eager_providers_are_created_when_starting_app_context(self):
        called = []
        self.appcontext.register("singleton", provider()(lambda: called.append(True)))
        self.appcontext.start()
        self.assertTrue(called)

    def test_lazy_providers_are_not_created_when_starting_app_context(self):
        called = []
        self.appcontext.register("singletonlazy", provider(lazy_init=True)(lambda: called.append(True)))
        self.appcontext.start()
        self.assertFalse(called)

    def test_error_raised_if_multiple_providers_register_with_same_name(self):
        self.appcontext.register("somename", lambda x,y: x*y)
        self.assertRaises(AlreadyRegistered, self.appcontext.register, "somename", lambda x,y:x*y)

    def test_register_config_registers_config_class_providers_as_appcontext_providers(self):
        self.appcontext.register_anonymous(mock_config_provider)
        self.appcontext.start()
        self.assertTrue(self.appcontext.provide("something"))

    def test_config_can_be_appcontext_aware(self):
        self.appcontext.register("MockConfig", mock_config_provider)
        self.appcontext.start()
        self.assertTrue(self.appcontext is self.appcontext.provide("MockConfig").context)



class TestAppContextAwareness(TestCase):
    def test_objects_offering_set_app_context_are_appcontext_aware(self):
        class SomeObj(object):
            def set_app_context(self, context):
                pass

        self.assertTrue(isinstance(SomeObj(), AppContextAware))

    def test_objects_not_offering_set_app_context_are_not_appcontext_aware(self):
        class SomeObj(object):
            pass

        self.assertFalse(isinstance(SomeObj(), AppContextAware))


#
#
#class TestAppContext(TestCase):
#    def test_appcontext_allows_retrieving_by_name(self):
#
#        class MockConf(object):
#            @singleton
#            def something(self):
#                return 1
#        MockConf = Configuration(MockConf)
#
#        context = AppContext(MockConf)
#        something = context.provide("something")
#        self.assertEquals(1, something)
#
#    def test_appcontext_supports_multiple_configs(self):
#        # TODO: this functionality might be overlapping to CompositeConfig.
#        # think about it.
#
#
#        class MockConf(object):
#            @singleton
#            def something(self):
#                return 1
#        MockConf = Configuration(MockConf)
#
#        class OtherConf(object):
#            @singleton
#            def otherthing(self):
#                return 2
#
#        OtherConf = Configuration(OtherConf)
#
#        context = AppContext(MockConf, OtherConf)
#        something = context.provide("something")
#        self.assertEquals(1, something)
#        otherthing = context.provide("otherthing")
#        self.assertEquals(2, otherthing)
#
#
#
#    def test_appcontext_fetches_objects_eagerly_when_required(self):
#        c = set()
#
#        class MockConf(object):
#            @singleton
#            def something(self):
#                c.add("something")
#
#            @singleton
#            def _private(self):
#                c.add("private")
#
#        MockConf = Configuration(MockConf)
#
#
#        conf = MockConf
#        context = AppContext(conf)
#        self.assertEquals(set(["something", "private"]), c)
#
#
#    def test_appcontext_fetches_objects_lazily_when_required(self):
#        c = []
#
#        class MockConf(object):
#            @singleton.lazy
#            def something(self):
#                c.append(True)
#        MockConf = Configuration(MockConf)
#
#
#        conf = MockConf
#        context = AppContext(conf)
#        self.assertEquals([], c)
#
#
#        MockConf = Configuration(MockConf)
#
#        context = AppContext(MockConf)
#        aware = context.provide("appcontextaware")
#        self.assertTrue(context is aware.app_context, "context wasn't injected correctly!")    def test_appcontext_gets_injected_on_aware_objects(self):
#        # TODO: think whether we need to use an ABC instead or as well.
#        class AppAwareObject(object):
#            app_context = None
#
#            def set_app_context(self, context):
#                self.app_context = context
#
#
#        class MockConf(object):
#            @singleton
#            def appcontextaware(self):
#                return AppAwareObject()
#
#
#
#class TestGlobalConfig(TestCase):
#    def test_global_config_falls_back_on_appcontext_factories(self):
#
#        class One(object):
#            def relies_on_other(self):
#                return self.other() * 2
#
#        class Other(object):
#            def other(self):
#                return 2
#
#        one = ContextConfiguration(One)
#        other = Configuration(Other)
#
#        context = AppContext(one, other)
#        self.assertEquals(4, context.provide("relies_on_other"))
#
#
#
#
#
#
