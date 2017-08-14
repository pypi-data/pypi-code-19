import birdjson
import birdyaml


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


def load_to_json(filename):
    return to_json(load_file(filename))


def load_to_yaml(filename):
    return to_yaml(load_file(filename))


def to_yaml(json_object):
    return birdyaml.YamlObject(**json_object.__dict__)


def to_json(yaml_object):
    return birdjson.JsonObject(**yaml_object.__dict__)
