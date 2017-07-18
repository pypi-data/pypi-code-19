import sys
if sys.version_info.major != 3 or sys.version_info.minor < 5:
    raise RuntimeError('Please use Python 3.5 or newer.')
    
from .cipher import (CaesarCipher, MultiplicativeCipher, AffineCipher, SubstitutionCipher,
                    VigenereCipher)
from .message import Message
from .alphabet import Alphabet, big, small, upper, lower
__version__ = '0.1.1'
