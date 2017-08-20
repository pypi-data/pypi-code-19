# -*- coding: utf-8 -*-

"""Module to provide an 'intelligent' list class

The IList class translates attribute access to the items it holds:

``l.<name> == IList([obj.<name> for obj in l])``

Import the IList class using ``from mtoolbox.ilist import IList``.

Example:

    >>> l = IList([complex(3, 4), complex(6)])
    >>> l.real
    [3.0, 6.0]

You can also use callable attributes of your objects:

    >>> l = IList([complex(3, 4), complex(6)])
    >>> l
    [(3+4j), (6+0j)]
    >>> l.conjugate()
    [(3-4j), (6-0j)]

You can add callbacks, for appending and removing objects. These
callbacks must accept two positional arguments - the list and the object.
The callbacks are called _after_ executing append or remove:

    >>> def on_append(l, x):
    ...     print("Adding %s to %s." % (x, l))
    >>> def on_remove(l, x):
    ...     print("Removing %s from %s." % (x, l))
    >>> l = IList(on_append=on_append, on_remove=on_remove)
    >>> l.append(3)
    Adding 3 to [3].
    >>> l.remove(3)
    Removing 3 from [].
    >>> def invalid_callback(l):
    ...     print(l)
    >>> l = IList(on_append=invalid_callback)
    Traceback (most recent call last):
    ...
    TypeError: on_append and on_remove must accept 2 positional arguments
    >>> l = IList(on_append=3)
    Traceback (most recent call last):
    ...
    TypeError: on_append and on_remove must accept 2 positional arguments

    >>> def valid_callback(l=[], x=5):
    ...     pass
    >>> def valid_callback2(l, x=5, y=3):
    ...     pass
    >>> l = IList(on_append=valid_callback, on_remove=valid_callback2)

Be aware, that only attribute names, that are not used by the list class
are overwritten, so if list implemented a attribute name, you can't use
it in this way. The following code doesn't work, because list implements
'__add__' (so the result is NOT [4, 5] as one could expect):

    >>> l = IList([1, 2])
    >>> l + 3
    Traceback (most recent call last):
    ...
    TypeError: can only concatenate list (not "int") to list

If you wish to access attributes with these names, you can use
:func:`IList.getattr` (see method documentation).

You can also apply any function to the items of an IList by
calling :func:`IList.apply` (see method documentation).
"""

import doctest
import inspect

class IList(list):
    """'intelligent' list object

    Args:
        iterable (iterable): The
        on_append (callable): callback(list, item) for append()
        on_remove (callable): callback(list, item) for remove()

    Returns:
        IList: An :class:`IList` instance

    Note:
        Both callbacks must accept two positional arguments
    """
    def __init__(self, iterable=None, on_append=None, on_remove=None):
        """Create new IList instance
        """
        # check on_append and on_remove and save them
        if on_append is None:
            on_append = lambda l, x: None
        if on_remove is None:
            on_remove = lambda l, x: None

        for func in on_append, on_remove:
            if not callable(func):
                raise TypeError(
                    "on_append and on_remove must accept 2 " + \
                    "positional arguments")

            spec = inspect.getargspec(func)
            maxarglen = len(spec.args)

            if spec.defaults:
                minarglen = maxarglen - len(spec.defaults)
            else:
                minarglen = maxarglen

            if not minarglen <= 2 <= maxarglen:
                raise TypeError(
                    "on_append and on_remove must accept 2 " + \
                    "positional arguments")

        self.__on_append = on_append
        self.__on_remove = on_remove

        # init list
        if iterable is not None:
            list.__init__(self, iterable)
        else:
            list.__init__(self)

        # run on_append on all given objects
        for value in self:
            self.__on_append(self, value)

    def append(self, obj):
        """Add obj to IList

        Args:
            obj (object): object to append to list

        Returns:
            None

        Usage:
            >>> l = IList()
            >>> l
            []
            >>> l.append(3)
            >>> l
            [3]
        """
        list.append(self, obj)
        self.__on_append(self, obj)

    def apply(self, func, *args, **kwargs):
        """Apply func to the items of this IList

        Args:
            func (callable): function to apply to this IList's items
            args (iterable): additional arguments for func
            kwargs (dict)  : additional keyword arguments for func

        Returns:
            IList: An :class:`IList` instance

        Usage:
            >>> def f(x, pow=2):
            ...     return x**pow
            >>> l = IList([0, 1, 2, 3, 4, 5])
            >>> l.apply(f, pow=3)
            [0, 1, 8, 27, 64, 125]
        """
        return IList([func(x, *args, **kwargs) for x in self])

    def getattr(self, name):
        """

        Args:
            name (str): name of the items attributes to access

        Returns:
            IList: An IList instance

        Usage:
            >>> l = IList([3, 5, 4])
            >>> l.getattr('__add__')(2)
            [5, 7, 6]
        """
        return IList([getattr(obj, name) for obj in self])

    def remove(self, obj):
        """Remove obj from IList

        Args:
            obj (object): object to remove from list

        Returns:
            None

        Usage:
            >>> l = IList([8])
            >>> l
            [8]
            >>> l.remove(8)
            >>> l
            []
            >>> l.remove(6)
            Traceback (most recent call last):
            ...
            ValueError: list.remove(x): x not in list
        """
        list.remove(self, obj)
        self.__on_remove(self, obj)

    def __getattr__(self, name):
        return IList([getattr(obj, name) for obj in self])

    def __call__(self, *args, **kwargs):
        return IList([obj(*args, **kwargs) for obj in self])

if __name__ == '__main__':
    doctest.testmod()
