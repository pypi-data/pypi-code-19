#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import, division, print_function
import datetime, time, requests

from enum import Enum

class Compression(Enum):
	NONE = 1
	GZIP = 2
	ZLIB = 3

class Subset(Enum):
	TRAIN = 1
	TEST = 2
	VALIDATION = 3

compression_suffix = {
	Compression.NONE: '',
	Compression.GZIP: 'gzip',
	Compression.ZLIB: 'zlib'
}

subset_suffix = {
	Subset.TRAIN:      'train',
	Subset.TEST:       'test',
	Subset.VALIDATION: 'validation'
}
