import unittest as ut

from tests._utils._timer import Timer
from drivelink import cached
#from Process import freeze_support


def uncachedFib(a):
    if a in [0, 1]:
        return a
    if a < 0:
        raise Exception("Reverse fibonacci sequence not implemented.")
    return uncachedFib(a - 1) + uncachedFib(a - 2)


def test_fib():
    assert uncachedFib(0) == 0
    assert uncachedFib(1) == 1
    assert uncachedFib(2) == 1
    assert uncachedFib(3) == 2
    assert uncachedFib(4) == 3
    assert uncachedFib(5) == 5


class cachedTest(ut.TestCase):
    c = None

    def setUp(self):
        @cached(self.id(), 1, 1)
        def fib(a):
            if a in [0, 1]:
                return a
            if a < 0:
                raise Exception("Reverse fibonacci sequence not implemented.")
            return fib(a - 1) + fib(a - 2)
        self.c = fib

    def test_fib(self):
        self.assertEqual(
            self.c(0), 0, "The zeroth element of the Fibonnaci sequence is 0, not {0}.".format(str(self.c(0))))
        self.assertEqual(
            self.c(1), 1, "The first element of the Fibonnaci sequence is 1, not {0}.".format(str(self.c(1))))
        self.assertEqual(
            self.c(2), 1, "The second element of the Fibonnaci sequence is 1, not {0}.".format(str(self.c(2))))
        self.assertEqual(
            self.c(3), 2, "The third element of the Fibonnaci sequence is 2, not {0}.".format(str(self.c(3))))
        self.assertEqual(
            self.c(4), 3, "The fourth element of the Fibonnaci sequence is 3, not {0}.".format(str(self.c(4))))
        self.assertEqual(
            self.c(5), 5, "The fifth element of the Fibonnaci sequence is 5, not {0}.".format(str(self.c(5))))

    def test_init(self):
        self.assertEqual(len(self.c.c), 0, "The cache was malformed.")
        self.assertEqual(self.c.f(0), uncachedFib(0), "The function was not entered correctly.")

    def test_cache(self):
        i = self.c(0)
        self.assertEqual(len(self.c.c), 1, "The value was not cached properly.")
        self.assertEqual(self.c(0), i, "The cached answer was incorrect.")

    def test_speed(self):
        with Timer() as t1:
            _ = uncachedFib(32)
        self.c.n = -1
        with Timer() as t2:
            _ = self.c(32)
        self.assertTrue(t2.interval < t1.interval,
                        "There isn't a speed up... This is useless then, I suppose.")
        with Timer() as t1:
            _ = self.c(32)
        self.assertTrue(t2.interval > t1.interval,
                        "There isn't a speed up... This is useless then, I suppose.")


if __name__ == '__main__':
    freeze_support()
    ut.main()
