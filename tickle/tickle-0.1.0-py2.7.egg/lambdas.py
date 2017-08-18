"""
Lambda serialization for tikcle.

Provides the classes required for serialization of lambdas and functions.
"""

import new
import uuid
import types
import marshal
import __builtin__

from tickle import Ticklable


class LambdaTicklable(Ticklable):
    """
    Ticklable for lambda types.
    """
    @classmethod
    def save(cls, tickler, obj):
        """
        Overload of `Ticklable.save`.
        """
        if obj.__name__ != "<lambda>":
            return tickler.save_global(obj)
        return super(LambdaTicklable, cls).save(tickler, obj)

    @staticmethod
    def dis_cells(func):
        """
        Extract cell key/values from a lambda closure.

        func -- the function object.

        Returns a dictionary of key/value pairs.
        """
        values = {}
        for k, n in enumerate(func.__code__.co_freevars):
            cell = func.__closure__[k]
            obj = type(lambda: 0)(
                (lambda x: lambda: x)(0).__code__, {}, None, None, (cell,)
            )()
            values[n] = obj
        return values

    @staticmethod
    def make_cells(**values):
        """
        Create cell objects from key/value pairs.

        **values -- the values.

        Returns a tuple containing the cell objects.
        """
        uid = str(uuid.uuid4()).replace("-", "")
        name = "make_cells_%s" % (uid,)

        code = "def %s():\n" % (name,)
        for k in values:
            code += "  %s = %s[%s]\n" % (k, name, repr(k),)
        code += "  return lambda: (%s)" % (", ".join(values.keys()),)

        globals()[name] = values
        exec(code)
        cells = locals()[name]().__closure__
        del globals()[name]

        return cells

    def __getstate__(self):
        """
        Overload of `Ticklable.__getstate__`.
        """
        co_globals = {}
        for x in __builtin__.__dict__:
            if x not in not_allowed_globals:
                co_globals[x] = __builtin__.__dict__[x]

        for k, v in self.data.__globals__.items():
            if v is self.data:
                continue

            if not (isinstance(v, types.ModuleType) or
                    isinstance(v, types.FunctionType) or
                    isinstance(v, type) or
                    isinstance(v, object) or
                    type(v) in [int, long, float, str, unicode]):
                continue

            if k in ["__builtins__"]:
                continue

            co_globals[k] = v

        return (marshal.dumps(self.data.__code__),
                co_globals,
                self.data.__defaults__,
                self.dis_cells(self.data),)

    def __setstate__(self, data):
        """
        Overload of `Ticklable.__setstate__`.
        """
        co_code, co_globals, co_defaults, co_cells = data

        co_codeobj = marshal.loads(co_code)
        co_closures = self.make_cells(**co_cells)

        self.data = new.function(co_codeobj, co_globals, "<lambda>", co_defaults, co_closures)


# The list of allowed globals
not_allowed_globals = [
    'Ellipsis',
    'NotImplemented',
]
