# encoding: utf-8

"""Release information about Dispatch."""

from __future__ import unicode_literals

from collections import namedtuple


version_info = namedtuple('version_info', ('major', 'minor', 'micro', 'releaselevel', 'serial'))(3, 0, 1, 'final', 0)
version = ".".join([str(i) for i in version_info[:3]]) + ((version_info.releaselevel[0] + str(version_info.serial)) if version_info.releaselevel != 'final' else '')

author = namedtuple('Author', ['name', 'email'])("Alice Bevan-McGregor", 'alice@gothcandy.com')
description = "Dispatch; a method to resolve path components to Python objects and enumerate available children using pluggable search mechanisms."
copyright = "2009-2017, Alice Bevan-McGregor and contributors"
url = 'https://github.com/marrow/web.dispatch'
