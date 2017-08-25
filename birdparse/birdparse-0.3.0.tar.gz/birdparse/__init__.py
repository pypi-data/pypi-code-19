import birdjson
from birdjson import JsonObject
import birdyaml
from birdyaml import YamlObject


class ParseException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


def load_file(filename):
    if filename.endswith('.yml') or filename.endswith('.yaml'):
        return birdyaml.load_file(filename)
    elif filename.endswith('.json'):
        return birdjson.load_file(filename)
    else:
        raise ParseException('unknown file format')


def write_yaml(obj, filename):
    obj = to_yaml(obj)
    with open(filename, 'w') as f:
        f.write(str(obj))


def write_json(obj, filename):
    obj = to_json(obj)
    with open(filename, 'w') as f:
        f.write(str(obj))


def load_file_to_json(filename):
    return to_json(load_file(filename))


def load_file_to_yaml(filename):
    return to_yaml(load_file(filename))


def to_yaml(obj):
    if type(obj) is YamlObject:
        return obj
    if type(obj) is JsonObject:
        return YamlObject(**obj.__dict__)
    return birdyaml.load_obj(obj)


def to_json(obj):
    if type(obj) is JsonObject:
        return obj
    if type(obj) is YamlObject:
        return JsonObject(**obj.__dict__)
    return birdjson.load_obj(obj)


def to_dict(obj):
    if type(obj) is JsonObject or type(obj) is YamlObject:
        return obj.__obj__()
    if type(obj) is dict:
        return obj
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    raise ValueError('invalid type')
