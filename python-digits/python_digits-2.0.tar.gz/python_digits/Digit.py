import logging
from .helpers import bad_value, debugit


class Digit(int):
    """Digit - a subclass of int designed to store a single digit between 0 and 9. A DigitEntry is
    formed by instantiation and passing an integer (or string representation) in the list:
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9. As a subclass of int, the DigitEntry obeys all integer operations
    such as multiply, add, etc."""
    def __new__(cls, value):
        """Instantiate a new digit."""

        bad_value_message = 'A digit must be a string representation or integer ' + \
                            'of a number between 0 (zero) and 9 (nine).'

        debugit(issuer='Digit', message='New digit instantiated. Value: {}'.format(value))

        _new_value = -1

        try:
            _new_value = int(value)
        except ValueError:
            pass

        if _new_value < 0 or _new_value > 9:
            bad_value(issuer='Digit', message=bad_value_message, value=value)

        obj = int.__new__(cls, _new_value)

        debugit(issuer='Digit', message='New digit created. Value: {}'.format(value))
        return obj
