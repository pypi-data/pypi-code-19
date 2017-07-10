import unittest

from aloe.cache import cached, store, get, delete, clear, dump

class TestCache(unittest.TestCase):
    def test_cached(self):
        store('foo', 0, '')
        self.assertTrue(cached('foo'))

    def test_get(self):
        store('bar', 1, 'A')
        store('bar', 1, 'B')
        store('bar', 1, 'C')
        store('bar', 0, 'X')
        store('bar', 0, 'Y')
        store('bar', 0, 'Z')

        # Toss in dupes.
        store('bar', 1, 'C')
        store('bar', 0, 'Z')
        store('bar', 0, 'Z')

        self.assertEqual(get('bar'), ['X', 'Y', 'Z', 'A', 'B', 'C'])

    def test_delete(self):
        store('X', 0, 'A')
        store('Y', 1, 'A')

        self.assertEqual(get('X'), ['A'])
        self.assertEqual(get('Y'), ['A'])

        delete('X', 'A')

        self.assertEqual(get('X'), [])
        self.assertEqual(get('Y'), ['A'])

        delete('Y', 'A')

        self.assertEqual(get('X'), [])
        self.assertEqual(get('Y'), [])

    def test_clear(self):
        store('X', 0, 'B')
        clear()
        self.assertFalse(cached('X'))

    def test_dump(self):
        clear()
        store('X', 1, 'A')
        store('X', 0, 'B')
        store('X', 1, 'C')
        store('Y', 0, 'C')
        store('Y', 1, 'A')

        for path, deps in dump():
            if path == 'X':
                self.assertEqual(deps, ['B', 'A', 'C'])
            elif path == 'Y':
                self.assertEqual(deps, ['C', 'A'])

if __name__ == '__main__':
    unittest.main()
