from future.utils import with_metaclass

class FastEnumMeta(type):

    def __new__(metacls, name, bases, attrs):
        _members = []
        for attr in attrs:
            if not attr.startswith('_'):
                _members.append(attr)

        klass = type.__new__(metacls, name, bases, attrs)

        super(metacls, klass).__setattr__('_members', _members)

        return klass

    def __setattr__(cls, attr, value):
        raise AttributeError("can't set attribute {}".format(attr))

    @property
    def members(cls):
        return cls._members


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
