"""
Advanced serialization library for Python 2.7+.

This library allows one to serialize more advanced types, such as lambdas, modules
and builtins. It mirrors the `pickle` module with more advanced features.
"""

import types
import pickle
from StringIO import StringIO


# Project info
__version__ = '0.1.0'

# Extensions registration
dispatch = {}


class Ticklable(object):
    """
    Ticklable base class.
    """
    @classmethod
    def save(cls, tickler, obj):
        """
        Method called to create a picklable instance of the object.
        """
        return tickler.save_inst(cls(obj))

    def __getinitargs__(self):
        """
        Get the picklable init arguments.
        """
        return (None,)

    def __init__(self, obj):
        """
        Initialize the picklable.

        obj -- the object to pickle.
        """
        self.data = obj

    def __getstate__(self):
        """
        Get the serialized object data.
        """
        return None

    def __setstate__(self, data):
        """
        Inject the serialized data into the object.

        data -- the serialized data.
        """
        self.data = None


class Tickler(pickle.Pickler):
    """
    Custom pickler class with added debugging and logging.
    """
    def save(self, obj):
        """
        Overload of `pickle.Pickler.save`.
        """
        if type(obj).__module__ == "site":
            return pickle.Pickler.save(self, None)

        try:
            picklable = obj.__class__.__dict__["__picklable__"](obj)
            self.dispatch[obj.__class__] = picklable.save
        except (AttributeError, KeyError):
            pass

        result = pickle.Pickler.save(self, obj)

        return result


class Untickler(pickle.Unpickler):
    """
    Overload of `pickle.Unpickler` to support custom types.
    """
    def load_build(self):
        """
        Overload of `pickle.Unpickler.load_build`.
        """
        pickle.Unpickler.load_build(self)
        last = self.stack[-1]

        if isinstance(last, Ticklable):
            obj = self.stack.pop()
            self.stack.append(obj.data)


def dumps(obj):
    """
    Serialize an object.

    obj -- the object to serialize.

    Returns a serialized version of the object.
    """
    from tickle.builtins import TypeTicklable
    from tickle.builtins import ModuleTicklable
    from tickle.lambdas import LambdaTicklable

    local_dispatch = {
        types.LambdaType: LambdaTicklable,
        types.ModuleType: ModuleTicklable,
        types.EllipsisType: Ticklable,
        types.NotImplementedType: Ticklable,
        types.ClassType: TypeTicklable,
        types.TypeType: TypeTicklable,
    }

    stream = StringIO()
    tickler = Tickler(stream)
    for T, cls in dispatch.items() + local_dispatch.items():
        tickler.dispatch[T] = cls.save
    tickler.dump(obj)
    stream.seek(0)
    return stream.read()


def loads(data):
    """
    Unserializes an object.

    data -- the serialized object.

    Returns a copy of the original object.
    """
    stream = StringIO(data)
    untickler = Untickler(stream)
    untickler.dispatch[pickle.BUILD[0]] = Untickler.load_build
    return untickler.load()
