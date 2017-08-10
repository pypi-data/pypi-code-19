from collections import namedtuple, OrderedDict
from typing import Any


def make_nt(*args, **kwargs) -> Any:
    return namedtuple(*args, **kwargs)


def member() -> Any:
    return ...


class MetaNamedTuple(type):
    def __prepare__(cls, _):  # pylint: disable=no-self-use
        return OrderedDict()

    def __new__(mcs, name, bases, attrs) -> Any:
        if name == '_NamedTuple':
            return super().__new__(mcs, name, bases, attrs)

        filtered = [attr for attr in attrs
                    if attrs[attr] is ...]

        attrs = {n: attr
                 for n, attr in attrs.items()
                 if n not in filtered}

        nt = make_nt(name, filtered)
        return super().__new__(mcs, name, bases + (nt,), attrs)


class _NamedTuple(metaclass=MetaNamedTuple):
    @classmethod
    def _fields(cls):
        return super()._fields  # pylint: disable=no-member


NamedTuple = _NamedTuple  # type: Any  # silencing mypy
