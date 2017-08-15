# -*- coding: utf-8 -*-
# Copyright (c) Virtual Reality and Clinical Gait Analysis Laboratory

import abc
import csv

from .data_column import DataColumn


class _DataFile:
    __metaclass__ = abc.ABCMeta

    def __init__(self, file, header_row=0):
        self._columns = []
        self._headers = []
        self.load(file, header_row)

    @abc.abstractmethod
    def load(self, input):
        """Retrieve data from the input source"""

    @property
    def columns(self):
        return self._columns

    @property
    def headers(self):
        return self._headers

    def get(self, header):
        if header not in self.headers:
            raise ValueError('missing column')

        return self.columns[self.headers.index(header)]


class CSV(_DataFile):

    def load(self, file, header_row):
        self._columns = []
        self._headers = []

        with open(file, 'r') as f:
            reader = list(csv.reader(f))
            columns = range(0, len(reader[header_row]))
            for column in columns:
                column_data = []
                for row in reader:
                    try:
                        column_data.append(float(row[column]))
                    except ValueError:
                        column_data.append(row[column])
                self._headers.append(column_data[header_row])
                self._columns.append(
                    DataColumn(
                        column_data[header_row],
                        column_data[header_row + 1:]
                    )
                )


def load(file, header_row=0):
    if '.csv' in file:
        return CSV(file, header_row)
    else:
        raise ValueError('file type not supported')
