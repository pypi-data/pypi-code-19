
from enum import Enum

class AutoNumberedEnum(Enum):
    """
    Enum that is automatically numbered with increasing integers. Automatically ensures uniqueness of values.
    """

    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj