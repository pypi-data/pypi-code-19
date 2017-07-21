class FastEnumMeta(type):

    def __new__(cls, name, bases, attrs):
        return type.__new__(cls, name, bases, attrs)

    def __init__(cls, name, bases, attrs):
        return type.__init__(cls, name, bases, attrs)

    def __setattr__(cls, attr, value):
        raise Exception('Cannot reassign member value.')


class FastEnum:

    """
    Fast and simple Enum implementation.

    .. code-block:: python
        class MyEnum(FastEnum):

            MEMBER = 'value'
            OTHER_MEMBER = 0

        MyEnum.MEMBER
    """

    __metaclass__ = FastEnumMeta
