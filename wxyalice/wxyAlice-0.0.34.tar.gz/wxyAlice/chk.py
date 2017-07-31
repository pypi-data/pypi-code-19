from jsonschema import validate
from jsonschema import FormatError, ValidationError
from sanic.exceptions import InvalidUsage


class Chk(object):
    def __init__(self, schema):
        self.schema = schema

    def Run(self, data):
        try:
            validate(data, self.schema)
        except ValidationError or FormatError as e:
            raise InvalidUsage(e.message)
