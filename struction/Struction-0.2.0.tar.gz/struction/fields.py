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
from struction.util import cast_type

class _Arg(object):
    def __init__(self, v):
        self.value = v


class default(_Arg):
    pass


class Field(object):
    def __init__(self, *args):
        self.types = []

        self.default = None

        for arg in args:
            if issubclass(type(arg), _Arg):
                setattr(self, arg.__class__.__name__, arg.value)
            else:
                self.types.append(arg)

        if self.default is not None and type(self.default) not in self.types:
            raise TypeError("Default field value must match one of field type(s)")
        if len(self.types) == 0:
            raise TypeError("No type specified for field")

    def __repr__(self):
        return "<{} default={!r}>".format(" ".join(t.__name__ for t in self.types), self.default)

    def match(self, value, typecasting=False):
        if value is None:
            return

        if typecasting:
            value = cast_type(value, *self.types)

        if type(value) not in self.types:
            raise TypeError("Field value must match one of field type(s)")

        return value

