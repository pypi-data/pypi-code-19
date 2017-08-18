from __future__ import absolute_import, print_function, unicode_literals

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from dojo.transform import Transform


class Validate(Transform):

    def __init__(self, schema, *args, **kwargs):
        self.schema = schema
        super(Validate, self).__init__(*args, **kwargs)

    def process(self, row):
        try:
            return self.validate_schema(row, self.schema)
        except ValidationError as e:
            raise ValueError('Validate failed with %s for %s' % (e.message, row))

    def validate_schema(self, row, schema):
        validate(row, schema)
        return row
