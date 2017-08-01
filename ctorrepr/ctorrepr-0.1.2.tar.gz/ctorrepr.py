# -*- coding: utf-8 -*-

"""Main module."""

__author__ = """Eugene M. Kim"""
__email__ = 'astralblue@gmail.com'
__version__ = '0.1.2'


class CtorRepr(object):
    """A mix-in that provides :py:meth:`object.__repr__()` from ctor arguments.

    Examples::
        >>> class X(CtorRepr):
        ...     def __init__(self, x1='x1', x2='x2', *poargs, **kwargs):
        ...         super().__init__(*poargs, **kwargs)
        ...         self.x1 = x1
        ...         self.x2 = x2
        ...     def _collect_repr_args(self, poargs, kwargs):
        ...         super()._collect_repr_args(poargs, kwargs)
        ...         poargs[:0] = self.x1, self.x2
        >>> class Y(CtorRepr):
        ...     def __init__(self, *y, **kwargs):
        ...         super().__init__(**kwargs)
        ...         self.y = y          # completely consumes positional args
        ...     def _collect_repr_args(self, poargs, kwargs):
        ...         super()._collect_repr_args(poargs, kwargs)
        ...         poargs[:0] = self.y
        >>> class Z(CtorRepr):
        ...     def __init__(self, *poargs, zk='zk', **kwargs):
        ...         super().__init__(*poargs, **kwargs)
        ...         self.zk = zk
        ...     def _collect_repr_args(self, poargs, kwargs):
        ...         super()._collect_repr_args(poargs, kwargs)
        ...         kwargs.update(zk=self.zk)
        >>> class W(X, Y, Z):
        ...     def __str__(self):
        ...         return repr(self)
        >>> print(' '.join(t.__name__ for t in W.mro()))
        W X Y Z CtorRepr object
        >>> print(W())
        W('x1', 'x2', zk='zk')
        >>> print(W(24))
        W(24, 'x2', zk='zk')
        >>> w = W(24, 25, 'y1', 'y2')
        >>> w.y
        ('y1', 'y2')
        >>> print(w)
        W(24, 25, 'y1', 'y2', zk='zk')
        >>> print(W(zk=100))
        W('x1', 'x2', zk=100)

    """

    __slots__ = ()

    def __repr__(self):
        """Return a machine-readable description.

        Collect all positional and keyword arguments using
        `_collect_repr_args()` and use it along with the class name.
        """
        poargs = []
        kwargs = {}
        self._collect_repr_args(poargs, kwargs)
        arg_strs = []
        if poargs:
            arg_strs.append(', '.join('{!r}'.format(arg) for arg in poargs))
        if kwargs:
            arg_strs.append(', '.join('{}={!r}'.format(k, v)
                                      for k, v in kwargs.items()))
        arg_str = ', '.join(arg_strs)
        return '{}({})'.format(self.__class__.__name__, arg_str)

    def _collect_repr_args(self, poargs, kwargs):
        """Collect all the args and kwargs for the constructor.

        Used by `__repr__()`.

        Subclasses wishing to include constructor arguments in the repr output
        must implement this method.  The implementation should first thunk to
        super(), then update *poargs* and *kwargs*.

        :param `list` poargs: positional arguments.
        :param `dict` kwargs: keyword arguments.
        """
