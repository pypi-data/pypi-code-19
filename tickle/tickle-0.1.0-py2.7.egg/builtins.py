"""
Builtins module for tickle.

This module provides support for serializing built-in types likes types and modules.
"""

import types

from tickle import Ticklable


class TypeTicklable(Ticklable):
    """
    Ticklable for built-in types.
    """
    @classmethod
    def save(cls, tickler, obj):
        """
        Method called to create a pickable instance of the object.
        """
        if obj.__module__ != "__builtin__":
            return tickler.save_global(obj)
        return super(TypeTicklable, cls).save(tickler, obj)

    def __getstate__(self):
        """
        Overload of `Ticklable.__getstate__`.
        """
        for k, v in types.__dict__.items():
            if v == self.data:
                return k

    def __setstate__(self, data):
        """
        Overload of `Ticklable.__setstate__`.
        """
        try:
            self.data = types.__dict__[data]
        except KeyError:
            pass


class ModuleTicklable(Ticklable):
    """
    Ticklable for module types.
    """
    def __getstate__(self):
        """
        Overload of `Ticklable.__getstate__`.
        """
        return self.data.__name__

    def __setstate__(self, data):
        """
        Overload of `Ticklable.__setstate__`.
        """
        parts = data.split(".")
        if len(parts) > 1:
            name = parts[0:-1]
            attr = parts[-1]
            obj = __import__(".".join(name), fromlist=[attr])
            self.data = getattr(obj, attr)
        else:
            self.data = __import__(parts[0])
