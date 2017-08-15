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
    if type(obj) is not YamlObject:
        obj = to_yaml(obj)
    with open(filename, 'w') as f:
        f.write(str(obj))


def write_json(obj, filename):
    if type(obj) is not JsonObject:
        obj = to_json(obj)
    with open(filename, 'w') as f:
        f.write(str(obj))


def load_to_json(filename):
    return to_json(load_file(filename))


def load_to_yaml(filename):
    return to_yaml(load_file(filename))


def to_yaml(json_object):
    return YamlObject(**json_object.__dict__)


def to_json(yaml_object):
    return JsonObject(**yaml_object.__dict__)
