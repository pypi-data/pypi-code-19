from __future__ import absolute_import, print_function, unicode_literals

from datetime import datetime

from dojo.transform import Transform


class Conform(Transform):

    def __init__(self, schema, *args, **kwargs):
        self.schema = schema
        super(Conform, self).__init__(*args, **kwargs)

    def process(self, row):
        return self.conform_schema(row, self.schema)

    def conform_schema(self, row, schema):
        def remove_nulls(obj):
            if isinstance(obj, dict):
                obj = {key: remove_nulls(value) for key, value in obj.items() if value is not None}
            elif isinstance(obj, list):
                obj = [remove_nulls(value) for value in obj if value is not None]
            return obj
        row = remove_nulls(row)
        for key, value in row.items():
            if isinstance(value, datetime):
                row[key] = value.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            if key not in schema['properties'].keys():
                del row[key]
        return row
