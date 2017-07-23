from mvpoly.util.cached_property import cached_property
import unittest

class Example(object) :

    def __init__(self):
        self._count = 0

    @property
    def count(self):
        self._count += 1
        return self._count

    @cached_property
    def cached_count(self):
        return self.count


class TestCachedProperty(unittest.TestCase):

    # check that the counting property increments

    def test_counter(self):
        example = Example();
        self.assertEqual(example.count, 1)
        self.assertEqual(example.count, 2)
        self.assertEqual(example.count, 3)

    # check that the cached counter version caches

    def test_cached_property_caches(self):
        example = Example();
        self.assertEqual(example.cached_count, 1)
        self.assertEqual(example.cached_count, 1)

    # check that assigning a cached property raises

    def test_cached_assign_raises(self):
        example = Example();
        self.assertEqual(example.cached_count, 1)
        with self.assertRaises(AttributeError):
            example.cached_count = 7

    # check that del(eting) a cached property means the
    # next access recalculates it

    def test_cached_delete_racalculates(self):
        example = Example();
        self.assertEqual(example.cached_count, 1)
        del example.cached_count
        self.assertEqual(example.cached_count, 2)
