"""
Defines the Singleton metaclass available through :class:`objecttools.Singleton`
"""

__all__ = ('Singleton',)


class Singleton(type):
    """A metaclass for defining singletons"""
    def __new__(mcs, name, bases, dict):
        """
        Create a new :class:`Singleton` instance

        :param name: Name of the new class
        :type name: str
        :param bases: Base classes of the new class
        :type bases: Tuple[type, ...]
        :param dict: Attributes of the new class
        :type dict: Dict[Str, Any]
        :return: A new class of type Singleton
        :rtype: Singleton
        """
        return super(Singleton, mcs).__new__(mcs, name, bases, dict)

    def __init__(cls, name, bases, dict):
        """
        Instantiate a :class:`Singleton` class

        :param name: Name of the new class
        :type name: str
        :param bases: Base classes of the new class
        :type bases: Tuple[type, ...]
        :param dict: Attributes of the new class
        :type dict: Dict[Str, Any]
        :return: None
        :rtype: NoneType
        """
        super(Singleton, cls).__init__(name, bases, dict)
        old_new = cls.__new__
        __init__ = cls.__init__
        this_cls = cls

        def __new__(cls=None):
            self = old_new(this_cls)
            __init__(self)
            this_cls.__self__ = self

            def __new__(cls=None):
                return self

            this_cls.__new__ = staticmethod(__new__)
            return self

        cls.__new__ = staticmethod(__new__)

    @classmethod
    def create(mcs, name, dict=None, object_name=None):
        """
        Create a new :class:`Singleton` class

        :param name: Name of the new class (Used in its __repr__ if no object_name)
        :type name: str
        :param dict: Optional dictionary of the classes' attributes
        :type dict: Optional[Dict[str, Any]]
        :param object_name: Name of an instance of the singleton. Used in __repr__.
        :type object_name: Optional[str]
        :return: A new Singleton instance
        :rtype: Singleton
        """
        if dict is None:
            dict = {}
        _repr = name + '()' if object_name is None else object_name

        def __repr__(self=None):
            return _repr
        dict.setdefault('__repr__', __repr__)
        return mcs(name, (object,), dict)

    @classmethod
    def as_decorator(mcs, cls):
        """
        Use :class:`Singleton` as a decorator for Python 2/3 compatibility::

            @Singleton.as_decorator
            class SingletonType(object):
                def __repr__(self):
                    return 'singleton'

            singleton = SingletonType()

        :param cls: Class to become a singleton
        :type cls: type
        :return: The new singleton
        :rtype: Singleton
        """
        return mcs(cls.__name__, cls.__bases__, cls.__dict__.copy())

    def __repr__(cls):
        return cls.__name__
