#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

import os
import sys
from setuptools import setup
import wtools


url = "https://bitbucket.org/Moo7/wtools"
here = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(here,'README.md')) as f:
	long_description = f.read()


setup(
	name = "wtools",
	version = wtools.version,
	author = "Michel Mooij",
	author_email = "michel.mooij7@gmail.com",
	maintainer = "Michel Mooij",
	maintainer_email = "michel.mooij7@gmail.com",
	url = url,
	download_url = "%s/downloads/wtools-%s.tar.gz" % (url, wtools.version),
	description = "WAF build tools",
	long_description = long_description,
	packages = ["wtools"],
	install_requires = [],
	license = 'MIT',
	keywords = ["waf", "c", "c++", "eclipse", "make", "GNU indent"],
	platforms = 'any',
	classifiers = [
		"Development Status :: 4 - Beta",
		"Environment :: Console",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Operating System :: Microsoft :: Windows :: Windows 7",
		"Operating System :: Microsoft :: Windows :: Windows Vista",
		"Operating System :: Microsoft :: Windows :: Windows XP",
		"Operating System :: POSIX :: Linux",
		"Programming Language :: C",
		"Programming Language :: C++",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3.4",
		"Topic :: Software Development :: Build Tools",
		"Topic :: Software Development :: Embedded Systems",
		"Topic :: Utilities",
	],
)

