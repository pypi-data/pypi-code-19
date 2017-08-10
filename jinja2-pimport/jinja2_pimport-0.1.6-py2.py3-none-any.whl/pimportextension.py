# -*- coding: utf-8 -*-

from jinja2 import nodes
from jinja2.ext import Extension

def filter_pimport(module):
    return __import__(module)

class PImportExtension(Extension):
    def __init__(self, environment):
        super(PImportExtension, self).__init__(environment)

        environment.filters['pimport'] = filter_pimport
