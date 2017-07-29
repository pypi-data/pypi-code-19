from future.utils import with_metaclass


class FastEnumMeta(type):

    def __new__(cls, name, bases, attrs):
        __members = []
        for attr in attrs:
            if not attr.startswith('_'):
                __members.append(attr)

        cls.__members = tuple(__members)

        return type.__new__(cls, name, bases, attrs)

    def __init__(cls, name, bases, attrs):
        return type.__init__(cls, name, bases, attrs)

    def __setattr__(cls, attr, value):
        raise AttributeError("can't set attribute")

    @property
    def members(cls):
        return cls.__members


class FastEnum(with_metaclass(FastEnumMeta)):

    """
    Fast and simple Enum implementation.

    .. code-block:: python
        class MyEnum(FastEnum):

            MEMBER = 'value'
            OTHER_MEMBER = 0

        MyEnum.MEMBER
        myenum_members = MyEnum.members
    """
    pass
