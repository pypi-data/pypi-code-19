from __future__ import absolute_import, print_function, unicode_literals

import json

from dojo.transform import Transform


class ConvertFrom(Transform):

    def process(self, row):
        if isinstance(row, dict):
            return row
        return self.parse_from_json(row)

    def parse_from_json(self, row):
        return json.loads(row)
