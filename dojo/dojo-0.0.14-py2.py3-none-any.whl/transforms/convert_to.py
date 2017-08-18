from __future__ import absolute_import, print_function, unicode_literals

import io
import csv
import json

from dojo.transform import Transform


class ConvertTo(Transform):

    def __init__(self, format, *args, **kwargs):
        self.format = format
        super(ConvertTo, self).__init__(*args, **kwargs)

    def process(self, row):
        return self.convert_to(row, self.format)

    def convert_to(self, row, format):
        if format == 'json':
            return self.convert_to_json(row)
        elif format == 'csv':
            return self.convert_to_csv(row)
        else:
            return row

    def convert_to_json(self, row):
        return json.dumps(row, ensure_ascii=False)

    def convert_to_csv(self, row):
        f = io.BytesIO()
        w = csv.writer(f)
        w.writerow([self._encode_cell(v) for v in row])
        f.seek(0)
        row = f.read()
        f.close()
        return row.strip().decode('utf-8')

    def _encode_cell(self, v):
        if isinstance(v, (str, unicode)):
            return v.encode('utf-8')
        else:
            return v
