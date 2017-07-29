from future.utils import with_metaclass

class FastEnumMeta(type):

    def __new__(metacls, name, bases, attrs):
        _members = []
        _values = []
        for attr in attrs:
            if not attr.startswith('_'):
                _members.append(attr)
                _values.append(attrs[attr])

        klass = type.__new__(metacls, name, bases, attrs)

        super(metacls, klass).__setattr__('_members', tuple(_members))
        super(metacls, klass).__setattr__('_values', tuple(_values))

        return klass

    def __setattr__(cls, attr, value):
        raise AttributeError("can't set attribute {}".format(attr))

    def __contains__(cls, attr):
        return hasattr(cls, attr)

    def __iter__(cls):
        for member in cls.members:
            yield member, getattr(cls, member)

    @property
    def members(cls):
        return cls._members

    @property
    def values(cls):
        return cls._values

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
