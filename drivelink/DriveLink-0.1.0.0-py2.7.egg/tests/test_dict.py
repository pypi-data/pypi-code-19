import unittest as ut
from drivelink import Dict
#from Process import freeze_support


class dictTest(ut.TestCase):
    def test_dict(self):
        dct = Dict("test")
        for i in range(10):
            dct[i] = i
        for i in range(10):
            self.assertEqual(dct[i], i, "The " + i + " element should be itself, not " + dct[i])


if __name__ == '__main__':
    freeze_support()
    ut.main()
