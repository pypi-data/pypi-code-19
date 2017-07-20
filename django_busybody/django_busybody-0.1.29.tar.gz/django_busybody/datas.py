# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import codecs
import zipfile
from django.utils.encoding import force_bytes

import sys
if sys.version_info[0] < 3:
    from backports import csv
else:
    import csv


class CsvDataMixin(object):
    encoding = 'UTF-8'
    delimiter = ','

    def get_encoding(self):
        return self.encoding

    def get_delimiter(self):
        return self.delimiter

    def write_data(self, buf, rows=None, **kwargs):
        if rows is None:
            rows = self.get_rows()
        csv_writer = csv.writer(
            codecs.getwriter(self.get_encoding())(buf, errors='replace'),
            delimiter=self.get_delimiter())
        for row in rows:
            csv_writer.writerow(row)

    def read_data(self, buf):
        csv_reader = csv.reader(
            codecs.getreader(self.get_encoding())(buf, errors='replace'),
            delimiter=self.get_delimiter())
        for row in csv_reader:
            yield row


class ZipDataMixin(object):
    def write_data(self, buf, path_content_list=None, **kwargs):
        if path_content_list is None:
            path_content_list = self.get_files()
        with zipfile.ZipFile(buf, 'w') as zf:
            for path, content in path_content_list:
                zf.writestr(path, force_bytes(content))

    def read_data(self, buf):
        with zipfile.ZipFile(buf, 'r') as zf:
            for path in zf.namelist():
                yield path, zf.read(path)
