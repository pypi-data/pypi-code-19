# -*- coding: utf-8 -*-

import json as pjson
from json import JSONEncoder
from datetime import datetime, time
import decimal


class JSON(JSONEncoder):

    def default(self, o):
        if hasattr(o, '__json__') and callable(getattr(o, '__json__')):
            return o.__json__()

        if hasattr(o, '__dict__'):
            return o.__dict__

        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")

        if isinstance(o, time):
            return o.strftime("%H:%M:%S")

        if isinstance(o, decimal.Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return "%s" % o

        raise TypeError(repr(o) + " is not JSON serializable")

    @classmethod
    def stringify(cls, o, ensure_ascii=False, separators=(',', ':'), encoding='utf-8', **kws):
        return pjson.dumps(o, cls=cls, ensure_ascii=ensure_ascii, separators=separators, encoding=encoding, **kws)

    @classmethod
    def parse(cls, str, **kws):
        return pjson.loads(str, **kws)

    @classmethod
    def dict(cls, o, **kws):
        return cls.parse(cls.stringify(o, **kws))


