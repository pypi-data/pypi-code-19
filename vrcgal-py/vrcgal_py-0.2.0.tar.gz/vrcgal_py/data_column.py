# -*- coding: utf-8 -*-
# Copyright (c) Virtual Reality and Clinical Gait Analysis Laboratory


class DataColumn:

    def __init__(self, header, data):
        self._header = header
        self._data = data

    @property
    def header(self):
        return self._header

    @property
    def data(self):
        return self._data

    def __len__(self):
        return len(self.data)
