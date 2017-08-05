from pyrencode.settings.utils import int2byte

# The bencode 'typecodes' such as i, d, etc have been extended and
# relocated on the base-256 character set.
CHR_LIST = int2byte(59)
CHR_DICT = int2byte(60)
CHR_INT = int2byte(61)
CHR_INT1 = int2byte(62)
CHR_INT2 = int2byte(63)
CHR_INT4 = int2byte(64)
CHR_INT8 = int2byte(65)
CHR_FLOAT32 = int2byte(66)
CHR_FLOAT64 = int2byte(44)
CHR_TRUE = int2byte(67)
CHR_FALSE = int2byte(68)
CHR_NONE = int2byte(69)
CHR_TERM = int2byte(127)

# Integer breakpoints
INT1_SIZE = 128
INT2_SIZE = 32768
INT4_SIZE = 2147483648
INT8_SIZE = 9223372036854775808


# Positive integers with value embedded in typecode.
INT_POS_FIXED_START = 0
INT_POS_FIXED_COUNT = 44

# Dictionaries with length embedded in typecode.
DICT_FIXED_START = 102
DICT_FIXED_COUNT = 25

# Negative integers with value embedded in typecode.
INT_NEG_FIXED_START = 70
INT_NEG_FIXED_COUNT = 32

# Strings with length embedded in typecode.
STR_FIXED_START = 128
STR_FIXED_COUNT = 64

# Lists with length embedded in typecode.
LIST_FIXED_START = STR_FIXED_START + STR_FIXED_COUNT
LIST_FIXED_COUNT = 64

ASCII = 'ascii'
UTF8 = 'utf8'
