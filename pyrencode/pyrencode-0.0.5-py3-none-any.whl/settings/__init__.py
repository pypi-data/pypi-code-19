from pyrencode.settings.utils import *
from pyrencode.settings.constants import *

# Default number of bits for serialized floats,
# either 32 or 64 (also a parameter for dumps()).
DEFAULT_FLOAT_BITS = 32

# Maximum length of integer when written as base 10 string.
MAX_INT_LENGTH = 64

# Whether strings should be decoded when loading
DECODE_UTF8 = False
