import json
import random
import sys
from .Digit import Digit
from .HexDigit import HexDigit
from .DigitWordAnalysis import DigitWordAnalysis
from .helpers import debugit


class DigitWord(object):
    """A DigitWord is a collection of Digit objects (see Digit). The collection can be any size (up to the
    maximum size of a list.) The DigitWord holds each Digit in a list (see word) and DigitWord(s)
    may be checked for equality and compared to another DigitWord (iterated analysis of the
    matches (none or loose) and the occurrence (one or more) of each Digit)"""

    _word = []
    DIGIT = 0
    HEXDIGIT = 1

    #
    # Instantiation
    #
    def __init__(self, *args, **kwargs):
        """Instantiate a new DigitWord by passing integers (or string representations) of DigitModel."""
        debugit(issuer='DigitWord', message='Instantiation started.')

        # Check if the word is set to decimal (digits from 0 to 9), hex (digits from 0 to F), or
        # if not specified, default to decimal for backwards compatibility.
        self.wordtype = DigitWord.DIGIT

        if kwargs:
            if 'wordtype' in kwargs:
                debugit(issuer='DigitWord',
                        message='wordtype found in parameters, value: {}'.format(kwargs['wordtype']))
                if kwargs['wordtype'] in [DigitWord.HEXDIGIT, DigitWord.DIGIT]:
                    self.wordtype = kwargs['wordtype']
                else:
                    debugit(issuer='DigitWord',
                            message='wordtype not valid: {}'.format(kwargs['wordtype']))
                    raise ValueError('wordtype must be set to DigitWord.DIGIT or DigitWord.HEXDIGIT')

        # Check if any numbers were passed or if this was an empty (i.e. []) DigitWord instantiation.
        if len(args) > 0:
            self.word = args

            debugit(issuer='DigitWord', message='Instantiation completed.')

    #
    # Override Methods
    #
    def __str__(self):
        """Return a string representation (e.g. '9999', 'ff90', or 'ffff' for a four DigitEntry word.)"""
        return_string = ''.join([str(w) for w in self.word])
        return return_string

    def __eq__(self, other):
        """Check the equality of the DigitWord against another DigitWord; to be equal, all DigitModel
        of the DigitWord must be in the exact position and they must be the same type; NB, this means
        a hex DigitWord of 1,2,3,4 would NOT equal a decimal DigitWord of 1,2,3,4.
        Returns True for an equality match, otherwise False. NOTE: can be invoked via
        digitWord1 == digitWord2"""

        # Check other is a DigitWord
        if not isinstance(other, DigitWord):
            return False

        # Check the DigitWords are the same type
        if other.wordtype != self.wordtype:
            return False

        return self.word == other.word

    def __iter__(self):
        """Iterate through each DigitEntry in the DigitWord"""

        # Note! Accessing the 'private' variable _word will retun 0x in front of hex digits. This
        # can be modified by iterating self.word (the 'public' getter), which converts '0xa' to 'a'.
        for w in self._word:
            yield w

    def __len__(self):
        """Return the length of the DigitWord (i.e. how many DigitModel there are.)"""
        return len(self._word)

    #
    # Properties
    #
    @property
    def word(self):
        """Property of the DigitWord returning (or setting) the DigitWord as a list of integers (or
        string representations) of DigitModel. The property is called during instantiation as the
        property validates the value passed and ensures that all digits are valid."""

        if self.wordtype == DigitWord.DIGIT:
            return self._word
        else:
            # Strip out '0x' from the string representation. Note, this could be replaced with the
            # following code: str(hex(a))[2:] but is more obvious in the code below.
            return [str(hex(a)).replace('0x', '') for a in self._word]

    @word.setter
    def word(self, value):
        """Property of the DigitWord returning (or setting) the DigitWord as a list of integers (or
        string representations) of DigitModel. The property is called during instantiation as the
        property validates the value passed and ensures that all digits are valid. The values can
        be passed as ANY iterable"""

        self._validate_word(value=value)

        _word = []

        # Iterate the values passed.
        for a in value:
            # Check the value is an int or a string.
            if not (isinstance(a, int) or isinstance(a, str) or isinstance(a, unicode)):
                raise ValueError('DigitWords must be made from digits (strings or ints) '
                                 'between 0 and 9 for decimal and 0 and 15 for hex')

            # This convoluted check is caused by the remove of the unicode type in Python 3+
            # If this is Python2.x, then we need to convert unicode to string, otherwise
            # we leave it as is.
            if sys.version_info[0] == 2 and isinstance(a, unicode):
                _a = str(a)
            else:
                _a = a

            # Create the correct type of Digit based on the wordtype of the DigitWord
            if self.wordtype == DigitWord.DIGIT:
                _digit = Digit(_a)
            elif self.wordtype == DigitWord.HEXDIGIT:
                _digit = HexDigit(_a)
            else:
                raise TypeError('The wordtype is not valid.')

            _word.append(_digit)

        self._word = _word

    #
    # Static Methods
    #
    @staticmethod
    def _validate_word(value):
        if not (isinstance(value, list) or isinstance(value, tuple)):
            raise TypeError('Expected list (or tuple) of integer digits or list of string representations!')

    #
    # Methods
    #
    def dump(self):
        """Dump the value of the DigitWord as a JSON representation of a list. The dumped JSON can be reloaded
        using obj.load(json_string)"""
        return json.dumps(self.word)

    def load(self, value):
        """Load the value of the DigitWord from a JSON representation of a list. The representation is
        validated to be a string and the encoded data a list. The list is then validated to ensure each
        digit is a valid digit"""

        if not isinstance(value, str):
            raise TypeError('Expected JSON string')

        _value = json.loads(value)
        self._validate_word(value=_value)
        self.word = _value

    def random(self, length=4):
        """Method to randomize the DigitWord to a given length; for example obj.random(length=4) would
        produce a DigitWord containing of four random Digits or HexDigits. The type of digit created
        is set by the wordtype."""
        if not isinstance(length, int):
            raise TypeError('DigitWord can only be randomized by an integer length')

        if self.wordtype == DigitWord.DIGIT:
            self._word = [Digit(random.randint(0, 9)) for i in range(0, length)]
        elif self.wordtype == DigitWord.HEXDIGIT:
            self._word = [HexDigit(str(hex(random.randint(0, 15))).replace('0x',''))
                          for i in range(0, length)]
        else:
            raise TypeError('wordtype is invalid.')

    def compare(self, other):
        """Compare the DigitWord with another DigitWord (other) and provided iterated analysis of the
        matches (none or loose) and the occurrence (one or more) of each DigitEntry in both
        DigitWords. The method returns a list of Comparison objects."""

        self._validate_compare_parameters(other=other)

        return_list = []
        for idx, digit in enumerate(other):
            dwa = DigitWordAnalysis(
                index=idx,
                digit=digit,
                match=(digit == self._word[idx]),
                in_word=(self._word.count(digit) > 0),
                multiple=(self._word.count(digit) > 1)
            )
            return_list.append(dwa)

        return return_list

    def _validate_compare_parameters(self, other):
        if not isinstance(other, DigitWord):
            raise TypeError('A DigitWord object can only be compared against another DigitWord object.')
        if len(self._word) != len(other.word):
            raise ValueError('The DigitWord objects are of different lengths and so comparison fails.')
        if other.wordtype != self.wordtype:
            raise ValueError('The DigitWord objects are different types and so comparison fails.')
