from __future__ import absolute_import, print_function, unicode_literals

import unittest

from ngen.singletons import Singleton


class Catalog(Singleton):

    registry = {}

    def register(self, name, value):
        self.registry[name] = value

Catalog()

class Mixin(object):

    def inspect(self):
        return self.registry.keys()


class Greetings(Catalog, Mixin):
    pass


class Workers(Catalog):
    pass


class SingletonTests(unittest.TestCase):
    def setUp(self):
        Workers._instance = None
        Greetings._instance = None

    def test_singleton_pattern(self):
        workers1 = Workers()
        workers2 = Workers()
        self.assertTrue(workers1 is workers2)

    def test_inheritance(self):
        workers = Workers()
        greetings = Greetings()
        self.assertFalse(workers is greetings)

    def test_registry_persists(self):
        workers = Workers()
        workers.register('foo', 'bar')
        self.assertEqual(workers.registry['foo'], 'bar')

        workers2 = Workers()
        self.assertEqual(workers2.registry['foo'], 'bar')

        greetings = Greetings()
        greetings.register('asdf', 'lkj')
        self.assertEqual(greetings.registry['asdf'], 'lkj')

        greetings2 = Greetings()
        self.assertEqual(greetings2.registry['asdf'], 'lkj')

    def test_repr(self):
        workers = Workers()
        self.assertIsInstance(repr(workers), str)


if __name__ == '__main__':
    unittest.main()
