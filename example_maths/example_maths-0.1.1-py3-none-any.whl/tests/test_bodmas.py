'''unit tests for example_maths'''

from unittest import TestCase

from example_maths import bodmas

class TestBodmasBadInput(TestCase):
    '''unit tests for bad input to add'''

    def test_is_float(self):
        '''add should fail given non-number variable'''
        self.assertRaises(bodmas.ArgumentError, bodmas.add, 1, "a")
        