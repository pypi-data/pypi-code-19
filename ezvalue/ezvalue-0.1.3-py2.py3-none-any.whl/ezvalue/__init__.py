"""An elegant and powerfull implementation of a value object.

This module provides base classes to easilly create new value
objects. Although value objects should in general be immutable
it is possible to create a mutable instance of a value object
when this is required.
"""


class _ValueBase:
    def _is_same_type(self, other, companion_class):
        return isinstance(other, (type(self), companion_class))

    def _is_equal(self, other, companion_class):
        if not self._is_same_type(other, companion_class):
            return False
        for name in self:
            if getattr(self, name) != getattr(other, name):
                return False
        return True

    def __iter__(self):
        """Return an iterable with the attribute names."""
        return iter(self._attributes)

    def __str__(self):
        """Return a string representation of the object."""
        attributes = ','.join('{}={}'.format(name, getattr(self, name))
                              for name in self)
        return '{}({})'.format(type(self).__name__, attributes)

    def __repr__(self):
        """Return a printable representation of the object.

        Generally when passing this representation to the eval
        function it will return a duplicate of the object, however
        this depends on the values of the attributes.
        """
        attributes = ','.join('{}={}'.format(name, repr(getattr(self, name)))
                              for name in self)
        return '{}({})'.format(type(self).__name__, attributes)

    def __hash__(self):
        """Return a hash of the values.

        The hash is computed by putting the values of the attributes
        in a hash and calculating the hash of that tuple.
        """
        return hash(tuple(getattr(self, attr) for attr in self))


class _MutableValueBase(_ValueBase):
    """Base class for the mutable version of a value.

    This is the base class for mutable versions of value objects and
    is not meant to instantiates directly. When defining a new value
    object the Mutable attribute is automatically set to a newly
    created subclass of this base class.

    A mutable value object has the same attributes as the immutable
    value object it is derived from, however the attributes are
    writable.

    Unlike an immutable value object where all the attributes must be
    supplied to the constructor, with a mutable value object it is
    possible to assign only a subset of attributes and assign the rest
    of the attributes later.

    Also unlike an immutable value object it is possible to define
    extra attributes like in normal python classes, for example to be
    used as temporary variables. These extra attributes will be
    ignored when creating an immutable value object from the mutable
    value object.
    """

    def __init__(self, source=None, **kwargs):
        """Create from a source object and/or keyword arguments.

        If source is given the attributes are initialized from
        equally named attributes of the source object. This means the
        class be initialized with for example an instance of the
        complementary Value class or with a named tuple. If the
        source object has attributes that are not defined in the
        Value class they are silently ignored.

        If additional keyword argument are given they will be assigned
        to the corresponding attributes. Unlike in the Value class
        keywords that do not correspond to defined attributes will be
        added to the class as new attributes. Any attributes that
        were also present in the source object will be overwritten
        by keyword arguments.

        Contrary to the immutable value object it is not an error if
        not all of the attributes are given, indeed one of the
        purposes of the mutable version of the value object is to
        allow object creation to happen in stages.
        """
        if source:
            for name in self._attributes:
                try:
                    setattr(self, name, getattr(source, name))
                except AttributeError:
                    pass
        for name, value in kwargs.items():
            setattr(self, name, value)

    def to_immutable(self):
        """Create an immutable value object from this mutable instance.

        Create an new instance of the complementary (immutable) Value
        class and pass 'self' as the source object. This has the effect
        of returning an immutable version of the object. Keep in mind
        that any assigned attributes that are not part of the Value's
        definition will not be part of the returned object.
        """
        return self.Immutable(self)

    def __eq__(self, other):
        """Test equality to another value object instance.

        An instance of a mutable value object is equal to another
        instance of the same value object or it's immutable companion
        class if and only if all attributes compare equal. Any
        additional attributes in a mutable class are ignored.

        An instance of a mutable value object is never equal to any
        other type, even if the attributes are the same.
        """
        return self._is_equal(other, self.Immutable)

    __hash__ = _ValueBase.__hash__


class ValueMeta(type):
    """Meta class for creating value objects.

    The ValueMeta class is responsible for setting several special
    class attributes on a value class. It is the meta class of the
    Value class, so normally the user should not have to specify
    a meta class when creating their own value objects. However if the
    user wishes to use their own meta class for a value object they
    must make sure their meta class inherits from this class.
    """

    def __init__(cls, name, bases, namespace):
        """Initialize the class.

        Set the list of attributes and generate a mutable
        companion class.
        """
        # pylint: disable = protected-access
        super().__init__(name, bases, namespace)
        attributes = {name for name in dir(cls)
                      if not name.startswith('_') and
                      not callable(getattr(cls, name))}
        attributes -= {'Mutable', 'to_mutable'}
        cls._attributes = attributes

        class SubclassedMutable(_MutableValueBase):
            pass

        cls.Mutable = SubclassedMutable
        cls.Mutable.__name__ = 'Mutable' + name
        cls.Mutable.Immutable = cls
        cls.Mutable._attributes = attributes


class Value(_ValueBase, metaclass=ValueMeta):
    '''Subclass this to define a new value object.

    The Value class is intended to be subclassed by the user to
    define a new value object. Alternatively the class can be
    instantiated directly to create an empty value object.

    To define a new value object the user should define a new class
    that inherits from this class. The attributes of the value object
    are defined by defining class attributes with the desired names
    in the subclass body. The value of the attributes should be a
    docstring describing the attribute. Valid attribute names are
    any valid python variable name not starting with an underscore
    except 'Mutable', 'to_mutable', 'Immutable' and 'to_immutable'.

    Example::

       class Point(ezvalue.Value):
           """Defines a cartesian point in 2D space."""

           x = """The x-coordinate in meters."""
           y = """The y-coordinate in meters."""


    Note: If the inherited class specifies a meta class than the
    meta class must inherit from ValueMeta.

    The resulting value object is an immutable object with the
    specified attributes. Attempting to assign a value to an
    attribute or creating a new attribute will raise an
    AttributeError.
    '''

    def __init__(self, source=None, **kwargs):
        """Create from a source object and/or keyword arguments.

        If the source argument is given the attributes will be
        initialized from equally named attributes in the source
        object. This for example allows the value object to be
        created from a named tuple. If the source object has fields
        that are not defined in the value object they will be ignored.

        Alternatively the objects can be initialized by supplying the
        names and values as keyword arguments.

        If both a source object and keyword arguments are given the
        keyword arguments supplement or overwrite the values from the
        source object. This allows the user to create a modified
        version of a value object by supplying the original as the
        source object and overwriting values as needed with
        keyword arguments.

        If the value object defines an attribute that is not present
        in either the source object or the keyword arguments then
        an AttributeError is raised. Extra keyword arguments that
        are not defined in the value object are silently ignored.
        """
        for name in self:
            if name in kwargs:
                value = kwargs[name]
            elif source:
                value = getattr(source, name)
            else:
                raise AttributeError("Attribute '{}' not specified."
                                     .format(name))
            setattr(self, name, value)

    def to_mutable(self):
        """Return a mutable copy of the value object.

        Create a new instance of the complementary mutable value
        object and pass 'self' as the source object.
        """
        return self.Mutable(source=self)

    def __eq__(self, other):
        """Test equality to another value object instance.

        An instance of a value object is equal to another instance of
        the same value object or it's mutable companion class if and
        only if all attributes compare equal. Any additional
        attributes in a mutable class are ignored.

        An instance of a value object is never equal to any other
        type, even if the attributes are the same. To compare to for
        example a named tuple, first create a new value object from
        the named tuple:

        >>> import collections
        >>> class MyValueObject(Value): foo = 'Test attribute'
        ...
        >>> my_value = MyValueObject(foo=1)
        >>> MyNamedTuple = collections.namedtuple('Foo', ('foo'))
        >>> my_value == MyValueObject(MyNamedTuple(foo=1))
        True
        """
        return self._is_equal(other, self.Mutable)

    __hash__ = _ValueBase.__hash__

    def __setattr__(self, name, value):
        """Raise AttributeError because object is immutable."""
        if name in self.__dict__ or name not in self:
            raise AttributeError('Object is immutable.')
        else:
            super().__setattr__(name, value)
