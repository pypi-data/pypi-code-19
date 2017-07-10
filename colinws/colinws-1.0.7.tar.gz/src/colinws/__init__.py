#!/usr/bin/env python
#-*- coding: utf-8 -*-
#Author: Colin
#Date: 2017-01-10
#Desc:
#


__author__ = 'Colin'
__version__ = '1.0.6'

from colinwsLogs import printLog, errorLog, warnLog
from colinwsDate import today, tommorrow, yesterday, daytime, dayBefore, dayAfter, firstAndLastDay
from colinwsEmail import sendEmail
from colinwsUtils import generate_passwd, getMD5, colorMsg

import sys

## private variables
_version = sys.version_info
_platform = sys.platform

## python2 or python3
is_py2 = (_version[0] == 2)
is_py3 = (_version[0] == 3)

## system 
is_linux = _platform.startswith('linux')
is_windows= _platform.startswith('win32')
is_osx = _platform.startswith('darwin')
is_linux = _platform.startswith('linux')


## difference between python2 and python3
if is_py2:
	unicode = unicode
	## basestring refer to str and unicode 
	basestring = basestring
	raw_input = raw_input
	xrange = xrange

if is_py3:
	unicode = str
	'''
	bytes and str in python3
	str.encode('utf-8') to bytes
	bytes.decode('utf-8') to str
	'''
	basestring = str
	raw_input = input
	xrange = range

