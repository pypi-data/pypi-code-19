from unittest import TestCase

from autoclass import validate, ValidationError


class TestAutoArgs(TestCase):

    def test_validate_simple(self):
        def is_even(x):
            return x % 2 == 0

        def gt(a):
            def gt(x):
                return x >= a

            return gt

        @validate(a=[is_even, gt(1)], b=is_even)
        def myfunc(a, b):
            print('hello')

        # -- check that the validation works
        myfunc(84, 82)
        with self.assertRaises(ValidationError):
            # a is not even
            myfunc(1,0)
        with self.assertRaises(ValidationError):
            # b is not even
            myfunc(2,1)
        with self.assertRaises(ValidationError):
            # a is not >= 1
            myfunc(0,0)

    def test_validate_error(self):
        """
        Checks that wrong validator names cant be provided
        :return: 
        """
        with self.assertRaises(ValueError):
            @validate(ab=[])
            def myfunc(a, b):
                print('hello')