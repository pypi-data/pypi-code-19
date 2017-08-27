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

from struction.fields import Field
from struction.util import indent, isfunc, cast_type



class _StructMeta(type):
    def __init__(cls, name, bases, clsdict):
        cls._fields = {}
        cls._fieldnames = []

        for fieldname in dir(cls):
            if not (fieldname.startswith("__") and fieldname.endswith("__") or
                            fieldname in ("_fields", "_fieldnames") or isfunc(getattr(cls, fieldname))):

                if not isinstance(cls.__dict__[fieldname], tuple):  # convert single items to tuples
                    setattr(cls, fieldname, (cls.__dict__[fieldname],))

                cls._fields[fieldname] = Field(*cls.__dict__[fieldname])

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
                setattr(self, name, kwargs[name])
            else:
                # use default

                if len(self._fields[name].types) == 1 and issubclass(self._fields[name].types[0], Struct) and \
                                self._fields[name].default is None:
                    setattr(self, name, self._fields[name].types[0]())  # auto init nested Structs
                else:
                    setattr(self, name, self._fields[name].default)

    def __str__(self):
        ret = ""

        kv = self.dict()

        for k in kv:
            ret += "{} = {!s}\n".format(k, kv[k])

        return self.__class__.__name__ + " {\n" + indent(ret, 4) + "}"

    def __repr__(self):
        ret = []

        kv = self.dict()

        for k in kv:
            ret.append("{}={!r}".format(k, kv[k]))

        return "{" + "{} {}".format(self.__class__.__name__, " ".join(ret)) + "}"

    def __setattr__(self, key, value):
        cls = self

        if key not in cls._fieldnames:
            raise KeyError("{!r} isn't a field for {!r}".format(key, self.__class__))
        field = cls._fields[key]

        super().__setattr__(key, field.match(value))

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
        """Returns dict of fields the struct has"""
        return self._fields


class TypecastingStruct(Struct):
    """
    Same as struct, but attempts to cast types. For example, if "5" is passed to a float field, it will become 5.0
    """
    def __setattr__(self, key, value):
        cls = self

        if key not in cls._fieldnames:
            raise KeyError("{!r} isn't a field for {!r}".format(key, self.__class__))

        field = cls._fields[key]
        super().__setattr__(key, field.match(value, typecasting=True))
