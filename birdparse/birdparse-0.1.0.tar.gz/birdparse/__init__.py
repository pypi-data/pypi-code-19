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


def to_yaml(json_object):
    return birdyaml.YamlObject(**json_object.__items__())


def to_json(yaml_object):
    return birdjson.JsonObject(**yaml_object.__items__())
