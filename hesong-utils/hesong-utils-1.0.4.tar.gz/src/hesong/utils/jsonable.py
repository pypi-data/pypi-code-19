# -*- coding: utf-8 -*-

from __future__ import absolute_import

import inspect
from datetime import date, datetime
from enum import Enum

from .stringhelper import to_str
from .jsonutils import *

__all__ = ['Jsonable']


class Jsonable:
    """
    :class:`Jsonable` is a class can covert all its simple data type properties into a JSON ready ``dict``
    """

    def jsonify(self):
        result = dict()

        def recursive_convert(val):
            if isinstance(val, Enum):
                return val.value
            elif isinstance(val, (type(None), str, int, float, bool)):
                return val
            elif isinstance(val, (datetime, date)):
                return val.isoformat()
            elif isinstance(val, Jsonable):
                return val.jsonify()
            elif isinstance(val, (tuple, list)):
                return [recursive_convert(x) for x in val]
            elif isinstance(val, dict):
                return {k: recursive_convert(v) for k, v in val.items() if isinstance(k, str)}

        for name, _ in inspect.getmembers(
                self.__class__,
                lambda x: x.fget is not None if isinstance(x, property) else False
        ):
            if not name.startswith('_'):
                result[name] = recursive_convert(getattr(self, name))
        return result

    def to_json(self, dumps=json_dumps):
        return dumps(self.jsonify())

    @classmethod
    def from_json(cls, data, excludes=None, loads=json_loads, *initargs, **initkwargs):
        if isinstance(data, (str, bytes)):
            data = loads(to_str(data))
        else:
            data = data or {}
        if not isinstance(data, dict):
            raise KeyError('Argument `value` should a `dict` or a JSON object `str`.')
        if isinstance(excludes, str):
            excludes = [excludes]
        excludes = excludes or []
        for x in excludes:
            try:
                del data[x]
            except KeyError:
                pass
        # TODO: recursive converse
        obj = cls(*initargs, **initkwargs)
        for name, _ in inspect.getmembers(
                cls,
                lambda x: x.fset is not None if isinstance(x, property) else False
        ):
            if not name.startswith('_'):
                setattr(obj, name, data.get(name))
        return obj
