# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import copy
from collections import Mapping, deque
from itertools import chain


class ContextPushPopContextManager(object):
    """
    Helper class for using context manager when pushing
    values in :py:class:`.Context`.

    Examples:

        ::

            >>> context = Context({'hello': 'earth'})
            >>> with context.push({'hello': 'mars'}) as context:
            ...     assert context['hello'] == 'mars'
            >>> assert context['hello'] == 'earth'
    """

    def __init__(self, context):
        self.context = context

    def __enter__(self):
        return self.context

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context.pop()


class Context(Mapping):
    """
    Container for stacked context data.

    A context provides a stack of scopes (represented by dictionaries).

    Statements such as with statement can push a new scope on the stack with
    data that should only be available inside clause. When the statement
    terminates, that scope can get popped off the stack again.

    >>> ctxt = Context({"user": "Fred", "city": "Bedrock"})
    >>> assert ctxt['user'] == 'Fred'
    >>> assert ctxt['city'] == 'Bedrock'
    >>> assert isinstance(ctxt.push({"user": "Barney"}), ContextPushPopContextManager)
    >>> assert ctxt['user'] == 'Barney'
    >>> assert ctxt['city'] == 'Bedrock'
    >>> assert ctxt.pop() == {'user': 'Barney'}
    >>> assert ctxt['user'] == 'Fred'
    """

    __slots__ = ('frames',)

    def __init__(self, context_data=None, **kwargs):
        """
        Initialize the template context with the dictionary
        """
        super(Context, self).__init__()
        if context_data is None:
            context_data = kwargs
        assert isinstance(context_data, Mapping), "Must init with a Mapping instance"

        context = self._get_base_context()
        context.update(context_data)

        self.frames = deque([context])

    def _get_base_context(self):
        """
        Hook which allows to customize what structure is used as base context.
        By default a new dict is returned.
        """
        return {}

    def __repr__(self):
        return repr(list(self.frames))

    def __contains__(self, key):
        """
        Return whether a variable exists in any of the scopes.

        :param key: the name of the variable
        """
        return self._find(key)[1] is not None

    has_key = __contains__

    def __delitem__(self, key):
        """
        Remove a variable from all scopes.

        :param key: the name of the variable
        """
        # Question: should we stop the del operations right before we get
        # to the top to not mutate original state??
        for frame in self.frames:
            if key in frame:
                del frame[key]

    def __getitem__(self, key):
        """
        Get a variables's value, starting at the current scope and going upward.

        :param key: the name of the variable
        :return: the variable value
        :raises KeyError: if the requested variable wasn't found in any scope
        """
        value, frame = self._find(key)
        if frame is None:
            raise KeyError(key)
        return value

    def __getattr__(self, key):
        """
        Get attribute's value, starting at the current scope and going upward.

        :param key: the name of the attribute
        :param value: the variable value
        """
        try:
            super(Context, self).__getattr__(key)
        except AttributeError:
            value, frame = self._find(key)
            if frame is not None:
                return value
            raise

    def __len__(self):
        """
        Return the number of keys in the context.

        :return: the number of keys
        """
        return len(self.keys())

    def __iter__(self):
        for k in self.keys():
            yield k

    def __setitem__(self, key, value):
        """
        Set a variable in the current scope.

        :param key: the name of the variable
        :param value: the variable value
        """
        self.frames[0][key] = value

    def __setattr__(self, key, value):
        """
        Set an attribute in the current scope.

        :param key: the name of the variable
        :param value: the variable value
        """
        if key in self.__slots__:
            super(Context, self).__setattr__(key, value)
        else:
            self.__setitem__(key, value)

    def __eq__(self, other):
        """
        Compare this context with other objects

        :param other: Object to compare self.frames with.
                      If the other object is a dict,
                      all frames are merged into a single dict
                      for comparison purposes.
        :type other: deque, list, tuple, dict
        :return: True if the two objects are equal, else False
        :raises TypeError: If the other object is of unsupported type
        """
        if isinstance(other, deque):
            return self.frames == other

        elif isinstance(other, (list, tuple)):
            return self.frames == deque(other)

        elif isinstance(other, Mapping):
            this = {}
            for frame in reversed(self.frames):
                this.update(frame)
            return this == other

        else:
            msg = 'Cannot compare instances of {} with {}'
            raise TypeError(msg.format(type(self), type(other)))

    def __ne__(self, other):
        """
        Returns negative result of ``__eq__``
        """
        return not self.__eq__(other)

    def __copy__(self):
        """
        Get a shallow copy of the context.

        This still returns an instance of ``Context`` however
        all frames are merged into a single frame.

        :return: Shallow copy returned as ``Context`` instance
        """
        return self.__class__({k: v for k, v in self.iteritems()})

    def __deepcopy__(self, memo=None):
        """
        Get a deep copy of the context.

        When copying, unlike ``__copy__``, this also preserves
        all context frames.

        :return: Deep copy of the context
        """
        # init new context
        # note the use of __class__
        # that ensures that copy of correct subclass is created
        new_context = self.__class__()

        # pop as we we insert a frame by default
        new_context.frames.popleft()

        # need to loop over frame by frame in reverse order and
        # copy all attributes in a frame to the new context
        for frame in reversed(self.frames):
            new_context.frames.appendleft({
                attr: copy.deepcopy(value) for attr, value in frame.items() if not callable(value)
            })

        return new_context

    def _find(self, key, default=None):
        """
        Retrieve a given variable's value and the frame it was found in.

        Intended primarily for internal use by directives.

        :param key: the name of the variable
        :param default: the default value to return when the variable is not
                        found
        """
        for frame in self.frames:
            if key in frame:
                return frame[key], frame
        return default, None

    def setdefault(self, key, default):
        """
        Same as dict's setdefault implementation.

        Return value under key if present, otherwise set value
        to default and return default value.
        """
        if key not in self:
            self[key] = default

        return self[key]

    def get(self, key, default=None):
        """
        Get a variable's value, starting at the current scope and going upward.

        :param key: the name of the variable
        :param default: the default value to return when the variable is not
                        found
        """
        for frame in self.frames:
            if key in frame:
                return frame[key]
        return default

    def iterkeys(self):
        """
        Return iterable of the name of all variables in the context.

        :return: an iterable of variable names
        """
        keys = set(chain.from_iterable(frame.keys() for frame in self.frames))
        return iter(keys)

    def keys(self):
        """
        Return the name of all variables in the context.

        :return: a list of variable names
        """
        return list(self.iterkeys())

    def itervalues(self):
        """
        Return iterable of values of all variables in the context.

        :return: an iterable of values
        """
        return (self.get(key) for key in self.keys())

    def values(self):
        """
        Return values of all variables in the context.

        :return: a list of values
        """
        return list(self.itervalues())

    def iteritems(self):
        """
        Return an iterable of ``(name, value)`` tuples for all variables in the context.

        :return: an iterable of variables with values
        """
        return ((key, self.get(key)) for key in self.keys())

    def items(self):
        """
        Return a list of ``(name, value)`` tuples for all variables in the context.

        :return: a list of variables with values
        """
        return list(self.iteritems())

    def copy(self):
        """
        Return a shallow copy of context

        :return: Shallow copy of the context
        """
        return self.__copy__()

    def update(self, mapping=None, **kwargs):
        """
        Update the context from the mapping provided.
        """
        self.frames[0].update(mapping, **kwargs)

    def push(self, data):
        """
        Push a new scope on the stack.

        Can also be used as a context manager which will pop the pushed
        values upon exiting context manager. For examples please refer
        to :py:class:`.ContextPushPopContextManager`.

        :param data: the data dictionary to push on the context stack.
        """
        if data is self:
            raise ValueError(
                'Cannot push context to itself.'
            )
        # For simplicity need to normalize the data to dict
        # since otherwise data can be another context
        # which will cause undesired recursion
        self.frames.appendleft(dict(data))
        return ContextPushPopContextManager(self)

    def pop(self):
        """
        Pop the top-most scope from the stack.

        :return: the frame popped from frames
        """
        return self.frames.popleft()
