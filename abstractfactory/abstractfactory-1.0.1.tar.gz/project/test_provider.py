import unittest

from abstract_factory import AbstractFactory

from mock import MockProviderFactory, MockProvider

class TestAbstractFactory(unittest.TestCase):
    def test_bad(self):
        abstractFactory = AbstractFactory()
        abstractFactory.set(MockProviderFactory)
        provider = abstractFactory.resolve(MockProvider, "bad") 
        try:
            result = provider.execute("nope")
        except NotImplementedError:
            pass
        else:
            self.fail('NotImplementedError not raised')

    def test_does_not_exist(self):
        abstractFactory = AbstractFactory()
        abstractFactory.set(MockProviderFactory)
        try:
            provider = abstractFactory.resolve(MockProvider, "does not exist") 
        except ValueError:
            pass
        else:
            self.fail('ValueError not raised')

    def test_execute_no_parameter(self):
        abstractFactory = AbstractFactory()
        abstractFactory.set(MockProviderFactory)
        provider = abstractFactory.resolve(MockProvider) 
        result = provider.execute() 

        self.assertEqual(result, "mock provider") 

    def test_execute_with_parameter(self):
        abstractFactory = AbstractFactory()
        abstractFactory.set(MockProviderFactory)
        provider = abstractFactory.resolve(MockProvider) 
        result = provider.execute("hello") 

        self.assertEqual(result, "hellomock provider") 

    def test_with_override_without_parameter(self):
        abstractFactory = AbstractFactory()
        abstractFactory.set(MockProviderFactory)
        provider = abstractFactory.resolve(MockProvider, "alt") 
        result = provider.execute() 

        self.assertEqual(result, "alternative mock provider") 

    def test_with_override_and_parameter(self):
        abstractFactory = AbstractFactory()
        abstractFactory.set(MockProviderFactory)
        provider = abstractFactory.resolve(MockProvider, "alt") 
        result = provider.execute("hi") 

        self.assertEqual(result, "hialternative mock provider") 

    def test_with_override_and_kwargs(self):
        abstractFactory = AbstractFactory()
        abstractFactory.set(MockProviderFactory)
        provider = abstractFactory.resolve(MockProvider, "alt", taco="keyword param") 
        result = provider.execute("hi")
        
        self.assertEqual(result, "hikeyword paramalternative mock provider") 

    def test_with_override_and_kwargs_and_paramkwargs(self):
        abstractFactory = AbstractFactory()
        abstractFactory.set(MockProviderFactory)
        provider = abstractFactory.resolve(MockProvider, "alt", taco="keyword param") 
        result = provider.execute("hi", burrito="parameter keyword param") 

        self.assertEqual(result, "hikeyword paramalternative mock providerparameter keyword param") 

if __name__ == '__main__':
    unittest.main()
