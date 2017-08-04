from future.utils import with_metaclass

class FastEnumMeta(type):

    def __new__(metacls, name, bases, attrs):
        slots = []
        _members = []
        _values = []
        _items = {}
        for attr in attrs:
            if not attr.startswith('_'):
                slots.append(attr)
                _members.append(attr)
                _values.append(attrs[attr])
                _items[attr] = attrs[attr]

        attrs['__slots__'] = tuple(slots)
        for member in _members:
            del attrs[member]

        klass = type.__new__(metacls, name, bases, attrs)

        super(metacls, klass).__setattr__('_members', frozenset(_members))
        super(metacls, klass).__setattr__('_values', tuple(_values))
        super(metacls, klass).__setattr__('_items', _items)

        return klass

    def __init__(cls, name, bases, attrs):
        type.__init__(cls, name, bases, attrs)

        for member, value in cls:
            super(FastEnumMeta, cls).__setattr__(member, value)

    def __setattr__(cls, attr, value):
        raise AttributeError("can't set attribute {}".format(attr))

    def __contains__(cls, attr):
        return hasattr(cls, attr)

    def __iter__(cls):
        for item in cls._items:
            yield (item, cls._items[item])

    def items(cls):
        return dict(cls.__iter__())

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
