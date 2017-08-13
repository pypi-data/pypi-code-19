#!/usr/bin/env python
# -*- coding: utf-8 -*-

from json import load
from os import path
from leankit import *


__version__ = "0.0.2"


class Mock():
    folder = path.join(path.dirname(path.realpath(__file__)), 'data')

    def get(self, url):
        log.debug(f'GET {url}')
        try:
            with open(path.join(self.folder, url.strip('/') + '.json')) as data:
                return load(data)
        except FileNotFoundError:
            raise ConnectionError('Server responded with code 404')


kanban.api = Mock()
