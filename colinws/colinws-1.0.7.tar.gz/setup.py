#!/usr/bin/env python
#-*- coding: utf-8 -*-
#Author: Colin
#Date: 2017-01-10
#Desc: package defined by self to deployment authomatically
#

#from distutils.core import setup
#, find_packages
from setuptools import setup, find_packages

setup(
	name = 'colinws',
	version = '1.0.7',
	url = 'http://www.jianshu.com/u/6d793fbacc88',
	license = 'MIT',
	author = 'Colin',
	author_email = 'bsply@126.com',
	description = 'tools for work',
	long_description = '',
	platforms = 'Linux,Unix',
	keywords = 'python, colin, Colin, colinws, Colinws, ColinwsTools',
	#packages = find_packages('src'),
	package_dir = {'':'src'},
	packages = ['colinws']
	#,'colinws.colinwsLogs', 'colinwsDate']
	#package_data = []
)
