# -*- coding: utf-8 -*-

__author__ = """Daniel Scheffler"""
__email__ = 'danschef@gfz-potsdam.de'
__version__ = '0.5.9'
__versionalias__ = 'v20170823.01'


from .baseclasses import GeoArray
from .masks import BadDataMask
from .masks import NoDataMask
from .masks import CloudMask

__all__=['GeoArray',
         'BadDataMask',
         'NoDataMask',
         'CloudMask'
         ]
