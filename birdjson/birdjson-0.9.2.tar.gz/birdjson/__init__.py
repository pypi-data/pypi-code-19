import json
import re
from datetime import datetime


class JsonObject(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]

    def __contains__(self, key):
        return key in self.__dict__

    def __repr__(self):
        return dumps(self)

    def __str__(self):
        return dumps(self)

    def __iter__(self):
        for k, v in self.__dict__.items():
            yield k, v

    def __len__(self):
        return len(self.__dict__.keys())

    def __keys__(self):
        return self.__dict__.keys()

    def __items__(self):
        return self.__dict__.items()

    def __values__(self):
        return self.__dict__.values()


def load_file(filename):
    with open(filename) as f:
        return load(f)


def load(fp):
    return _load(json.load(fp))


def loads(s):
    return _load(json.loads(s))


def load_obj(obj):
    return _load(obj)


def dumps(obj, **kwargs):
    return json.dumps(obj, default=lambda o: _json_default(o), **kwargs)


def makes(**kwargs):
    """Create a json string from arguments"""
    return dumps(JsonObject(**kwargs))


def _load(js):
    if type(js) is list:
        return _load_list(js)
    elif type(js) is dict:
        return _load_dict(js)
    return js


def _load_list(js):
    l = []
    for v in js:
        _append_value(l, v)
    return l


def _load_dict(js):
    g = JsonObject()
    for key in js:
        _inject_value(g, key, js[key])
    return g


def _append_value(parent, value):
    if type(value) is list:
        l = []
        for v in value:
            _append_value(l, v)
        parent.append(l)
    elif type(value) is dict:
        d = JsonObject()
        for k, v in value.items():
            _inject_value(d, k, v)
        parent.append(d)
    else:
        parent.append(value)


def _inject_value(parent, key, value):
    if type(value) is list:
        l = []
        for v in value:
            _append_value(l, v)
        parent.__dict__[_sanitize_key(key)] = l
    elif type(value) is dict:
        d = JsonObject()
        for k, v in value.items():
            _inject_value(d, k, v)
        parent.__dict__[_sanitize_key(key)] = d
    else:
        parent.__dict__[_sanitize_key(key)] = value


def _sanitize_key(key, safe_mode=False):
    k = str(key)
    if safe_mode:
        if re.match(r'^([0-9])', k):
            k = '_' + k
        k = k.replace(' ', '_').replace('-', '_')
    return k


def _json_default(o):
    if isinstance(o, datetime):
        return str(o)
    else:
        return o.__dict__
