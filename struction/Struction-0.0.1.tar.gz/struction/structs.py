"""
Copyright (c) 2017 James Patrick Dill

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from struction.util import isfunc
from struction.util import indent as _indent


class _StructMeta(type):
    def __init__(cls, name, bases, clsdict):
        cls._fields = {}
        cls._fieldnames = []

        for fieldname in dir(cls):
            if not (fieldname.startswith("__") and fieldname.endswith("__") or
                    fieldname in ("_fields", "_fieldnames") or isfunc(getattr(cls, fieldname))):
                field = cls.__dict__[fieldname]

                if type(field) == tuple:
                    if len(field) != 2:
                        raise TypeError(
                            "Fields with default values should be tuples with 2 items, e.g., FIELD = int, 1")
                    else:
                        field = list(field)
                        if not isinstance(field[0], list):
                            field[0] = [field[0]]

                        if type(field[1]) not in field[0]:
                            raise TypeError("Default field value should be instance of field type")
                        else:
                            cls._fields[fieldname] = (field[0], field[1])  # (type, default)
                else:
                    if not isinstance(field, list):
                        field = [field]

                    cls._fields[fieldname] = (field, None)  # (type, default)

                cls._fieldnames.append(fieldname)
                delattr(cls, fieldname)

        super(_StructMeta, cls).__init__(name, bases, clsdict)

    def __repr__(cls):
        return "<struct {!r}>".format(cls.__name__)


class Struct(object, metaclass=_StructMeta):
    """
    Struct superclass.
    """
    _fields = {}
    _fieldnames = []

    def __init__(self, **kwargs):
        """
        :keyword kwargs: Keyword values to assign to struct. Must match the struct's fields
        """
        cls = self

        for name in cls._fieldnames:
            if name in kwargs:
                # check if value matches type
                if (type(kwargs[name]) not in cls._fields[name][0]) and kwargs[name] is not None:
                    raise TypeError("Field {!r} must be instance of {}".format(name, " or ".join(
                        repr(t) for t in cls._fields[name][0])))

                setattr(self, name, kwargs[name])

            else:
                # use default

                if len(self._fields[name][0]) == 1 and issubclass(self._fields[name][0][0], Struct) and \
                        self._fields[name][1] is None:
                    setattr(self, name, self._fields[name][0][0]())  # auto init nested Structs
                else:
                    setattr(self, name, self._fields[name][1])

    def __str__(self):
        ret = ""

        kv = self.dict()

        for k in kv:
            ret += "{} = {!r}\n".format(k, kv[k])

        return self.__class__.__name__ + " {\n" + _indent(ret, 4) + "}"

    def __repr__(self):
        ret = []

        kv = self.dict()

        for k in kv:
            ret.append("{}={!r}".format(k, kv[k]))

        return "<struct {!r} {}>".format(self.__class__.__name__, " ".join(ret))

    def __setattr__(self, key, value):
        cls = self

        if key not in cls._fieldnames:
            raise KeyError("{!r} isn't a field for {!r}".format(key, self.__class__))

        if type(value) not in cls._fields[key][0] and value is not None:
            raise TypeError("Field {!r} must be instance of {}".format(key, " or ".join(
                str(t) for t in cls._fields[key][0])))

        super().__setattr__(key, value)

    def __delattr__(self, key):
        cls = self

        if key not in cls._fieldnames:
            raise KeyError("{!r} isn't a field for {!r}".format(key, self.__class__))

        setattr(self, key, None)

    def __iter__(self):
        return iter(self._fieldnames)

    def dict(self):
        """Returns dict of struct."""
        ret = {}
        for name in self._fieldnames:
            ret[name] = getattr(self, name)

        return ret

    def fields(self):
        """Returns list of fields the struct has"""
        return self._fieldnames


# --- TESTING --- #

class OnlyInt(Struct):
    field_0 = int
    field_1 = int


class Nested(Struct):
    abc = str
    nest = OnlyInt
