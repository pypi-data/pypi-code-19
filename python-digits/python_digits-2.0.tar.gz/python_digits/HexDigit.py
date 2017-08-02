import logging
from .helpers import debugit, bad_value


class HexDigit(int):
    """HexDigit - a subclass of int designed to store a single digit between 0 and 9. A DigitEntry is
    formed by instantiation and passing an integer (or string representation) in the list:
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, A, B, C, D, E, F. As a subclass of int, the DigitEntry obeys all
    integer operations such as multiply, add, etc."""

    def __new__(cls, value):
        """Instantiate a new digit."""

        bad_value_message = 'A hex digit must be a string representation or integer ' + \
                            'of a number between 0 (zero) and F (fifteen).'

        debugit(issuer='HexDigit', message='Value passed --> {}'.format(value))
        debugit(issuer='HexDigit', message='Value type   --> {}'.format(type(value)))
        _new_value = -1

        if isinstance(value, str):
            vlen = len(value)
            if vlen > 3:
                debugit(issuer='HexDigit', message='Value {} is too long!'.format(value))
                bad_value(issuer='Digit', message=bad_value_message, value=value)
            elif vlen > 1:
                if value[0:2] != '0x':
                    debugit(issuer='HexDigit', message='Value {} is longer than 1 and does not start 0x!'.format(value))
                    bad_value(issuer='Digit', message=bad_value_message, value=value)
                value = value[2:]
            if value.upper() > 'F':
                debugit(issuer='HexDigit', message='Value {} not a hex digit!'.format(value))
                bad_value(issuer='Digit', message=bad_value_message, value=value)
        elif isinstance(value, int):
            value = str(hex(value))
        else:
            debugit(issuer='HexDigit', message='Value {} passed is not a string or an int!'.format(value))
            bad_value(issuer='Digit', message=bad_value_message, value=value)

        try:
            _new_value = int(value, 16)
            debugit(issuer='HexDigit', message='Value converted to int. New value is {}, old was {}'.format(_new_value, value))
        except ValueError as ve:
            debugit(issuer='HexDigit', message='Value {} failed validation as a string! Exception: {}'.format(value, str(ve)))
            bad_value(issuer='Digit', message=bad_value_message, value=value)

        if _new_value < 0 or _new_value > 15:
            bad_value(issuer='Digit', message=bad_value_message, value=value)

        obj = int.__new__(cls, _new_value)
        return obj

    def __str__(self):
        return hex(self)
