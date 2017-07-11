from unittest import TestCase
from pydenji.config.pythonconfig import Configuration
from pydenji.config.provider import singleton, prototype, provider

class TestDuckConfiguration(TestCase):
    def test_any_object_with_get_public_providers_can_be_a_configuration(self):
        class Any(object):
            def get_public_providers(self):
                pass


        self.assertTrue(isinstance(Any(), Configuration))

class MyConf(Configuration):
    @provider(scope=prototype)
    def some_object(self, a):
        return a

    @provider(scope=singleton)
    def my_singleton(self):
        return 2

    def other_func(self):
        pass

conf = MyConf()

class TestConfiguration(TestCase):
    def test_default_configuration_returns_all_and_only_provider_names(self):
        self.assertEquals(set(["some_object", "my_singleton"]), set(conf.get_public_providers().keys()))

    def test_default_configuration_returns_provider_factories(self):
        names_providers = conf.get_public_providers()
        # suboptimal multiple assertion... but what should I use?
        self.assertEquals(conf.some_object, names_providers["some_object"])
        self.assertEquals(conf.my_singleton, names_providers["my_singleton"])