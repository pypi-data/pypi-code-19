#!/usr/bin/env python
# -*- coding: utf-8 -*-

from json import load
from os import path

import leankit
from leankit import *


__version__ = "0.0.3"


class Mock():
    folder = path.join(path.dirname(path.realpath(__file__)), 'data')

    def get(self, url):
        log.debug(f'GET {url}')
        try:
            filename = path.join(self.folder, url.lower().strip('/') + '.json')
            with open(filename) as data:
                return load(data)
        except FileNotFoundError:
            raise ConnectionError('Server responded with code 404')


leankit.api = leankit.kanban.api = Mock()
