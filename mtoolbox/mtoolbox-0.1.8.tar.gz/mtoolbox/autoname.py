# -*- coding: utf-8 -*-

"""Access an object's name as a property

Autoname is a data-descriptor, which automatically looks up the
name under which the object on which the descriptor is accessed
is known by.

Import the descriptor using ``from mtoolbox.autoname import Autoname``.

Example:

>>> class Object(object):
...     name = Autoname()
>>> obj1 = Object()
>>> obj1.name
'obj1'
>>> obj2 = Object()
>>> obj2.name
'obj2'

By default Autoname will return the outer-most name that was defined
for the object:

>>> class Object(object):
...     name = Autoname()
>>> def func(anobject):
...     return anobject.name
>>> o = Object()
>>> func(o)
'o'

You can change this behaviour by using the 'inner' keyword:

>>> class Object(object):
...     name = Autoname(inner=True)
>>> o = Object()
>>> def func(anobject):
...     return anobject.name
>>> func(o)
'anobject'

Note:
    Please be aware, that getting the inner-most name, is not what you
    want in most cases:

    >>> class Object(object):
    ...     name = Autoname(inner=True)
    ...     def printname(self):
    ...         print(self.name)
    >>> o = Object()
    >>> o.printname()
    self

    When in automatic mode (see the class documentation below) the
    descriptor will always return a name, that is in some callframe
    dictionary. If you delete a name, it will use another one, that
    is still in use:

    >>> class Object(object):
    ...     name = Autoname()
    >>> o = Object()
    >>> o.name
    'o'
    >>> g = o
    >>> del o
    >>> g.name
    'g'

    This can be helped a bit by using the 'bind' keyword argument and
    calling <object>.name with the name that should be used first:

    >>> class Object(object):
    ...     name = Autoname(bind=True)
    >>> o = Object()
    >>> o.name
    'o'
    >>> g = o
    >>> del o
    >>> g.name
    'o'

Warning:
    Defining multiple names for an object in the same call frame (which is
    easily said the same level of indention in your program) will
    cause undetermined behaviour, depending on the Python interpreter:

    >>> class Object(object):
    ...     name = Autoname()
    >>> o = Object()
    >>> g = o
    >>> o.name in ['o', 'g']
    True
"""

import doctest
import inspect


class Autoname(object):
    """Create a new Autoname descriptor

    Args:
        slot (str):   The instance attribute name
                      for explicit name assignment.
        inner (bool): Return the inner-most name of the object (or not)
        bind (bool):  Bind the descriptor to the first name it returns

    Returns:
        Autoname: An Autoname instance
    """

    def __init__(self, slot='__name', inner=False, bind=False):
        if not isinstance(slot, str) or not slot:
            raise TypeError("'slot' keyword must be an non-empty string.")
        self.slot = slot
        self.inner = inner
        self.bind = bind

    def __get__(self, theobject, objtype):
        """Return the name of theobject or None

        Returns:
            str or None: the name of the object

        Usage:
            >>> class Object(object):
            ...     name = Autoname()
            >>> obj = Object()
            >>> obj.name
            'obj'
            >>> obj.name = 'another name'
            >>> obj.name
            'another name'
        """
        val = getattr(theobject, self.slot, True)

        if isinstance(val, str):
            return val
        elif val is False or val is None:
            return None
        else:
            # If we really didn't find a name, we return None
            thename = None

            # There is at least one frame in the callstack, in which
            # the calling object is a local variable, so we climb up
            # the callstack, to find the name of the object.
            for count, frametuple in enumerate(inspect.stack()):
                # skip the first frame - this is our __get__
                if count == 0:
                    continue

                for name, obj in frametuple[0].f_locals.items():
                    # found a name, but keep searching in order to get
                    # the outer-most name unless inner == True
                    if obj is theobject:
                        thename = name
                        if self.inner:
                            self.__bind_if_wanted(theobject, thename)
                            return thename

            self.__bind_if_wanted(theobject, thename)
            return thename

    def __bind_if_wanted(self, theobject, thename):
        if self.bind:
            self.__set__(theobject, thename)

    def __set__(self, theobject, val):
        """Set the name of the theobject

        Args:
            theobject (object): The object to which's class
                                the descriptor is attached to

            val (str, bool or None): Sets the name to depending on the type:
                str sets the name to this str.
                False or None sets the name to None.
                True sets the name to automatically lookup.

        Returns:
            None

        Raises:
            TypeError if type(val) is invalid

        Usage:
            >>> class Object(object):
            ...     name = Autoname()
            >>> o1 = Object()
            >>> o2 = Object()
            >>> o1.name = 'k'
            >>> o2.name = 'm'
            >>> o1.name
            'k'
            >>> o2.name
            'm'
            >>> o1.name = True
            >>> o1.name
            'o1'
            >>> o1.name = False
            >>> str(o1.name)
            'None'
            >>> o1.name = 4
            Traceback (most recent call last):
            ...
            TypeError: Autoname must be set to str, bool, NoneType

            Note:
                Setting the name of an object to an explicit value
                will save that value as set the '__name' by default.
                You can change this by setting 'slot' on the Autoname
                descriptor:

                >>> class Object1(object):
                ...     name = Autoname()
                >>> class Object2(object):
                ...     name = Autoname(slot='__thename')
                >>> obj1 = Object1()
                >>> obj2 = Object2()
                >>> obj1.__name = 'an object'
                >>> obj2.__name = 'an object'
                >>> obj1.name = 'first object'
                >>> obj1.name
                'first object'
                >>> obj1.__name
                'first object'
                >>> obj2.name = 'second object'
                >>> obj2.name
                'second object'
                >>> obj2.__name
                'an object'
        """
        types = (str, bool, type(None))

        if not isinstance(val, types):
            raise TypeError("Autoname must be set to %s" % ", ".join(
                [t.__name__ for t in types]))

        setattr(theobject, self.slot, val)

if __name__ == '__main__':
    doctest.testmod()
