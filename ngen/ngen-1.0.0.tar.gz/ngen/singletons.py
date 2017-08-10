"""
This module contains a simple basis for inheritance enabled singletons.
"""
from __future__ import unicode_literals, absolute_import, print_function
from abc import ABCMeta

import six
from future.utils import python_2_unicode_compatible


class SingletonType(ABCMeta):
    """Ensures that each new subclass of the Singleton base class is "reset".
    """
    def __new__(mcs, name, bases, attrs):
        new_class = super(SingletonType, mcs).__new__(mcs, name, bases, attrs)
        parents = [base for base in bases if isinstance(base, SingletonType)]
        if parents:
            new_class._instance = None
        return new_class


@python_2_unicode_compatible
class Singleton(six.with_metaclass(SingletonType)):
    """Allows the singleton pattern to be inherited in the usual python style:
            class A(Singleton):
                pass

            class B(Singleton):
                pass

            a0 = A()
            a1 = A()
            a0 is a1  # True

            b = B()
            b is A()  # False
    It also exposes a initialize method on the instance level which can be used
    to characterize the singleton.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, id(self))
