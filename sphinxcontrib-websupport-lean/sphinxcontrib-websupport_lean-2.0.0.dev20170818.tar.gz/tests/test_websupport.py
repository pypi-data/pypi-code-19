# -*- coding: utf-8 -*-
"""
    test_websupport
    ~~~~~~~~~~~~~~~

    Test the Web Support Package

    :copyright: Copyright 2007-2017 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from sphinx.websupport import WebSupport
from sphinx.websupport.errors import DocumentNotFoundError
from sphinx.websupport.storage import StorageBackend
from sphinx.websupport.storage.differ import CombinedHtmlDiff
try:
    from sphinx.websupport.storage.sqlalchemystorage import Session
    from sphinx.websupport.storage.sqlalchemy_db import Node
    sqlalchemy_missing = False
except ImportError:
    sqlalchemy_missing = True

import pytest
from util import rootdir, tempdir


@pytest.fixture
def support(request):
    settings = {
        'srcdir': rootdir / 'root',
        # to use same directory for 'builddir' in each 'support' fixture, using
        # 'tempdir' (static) value instead of 'tempdir' fixture value.
        # each test expect result of db value at previous test case.
        'builddir': tempdir / 'websupport'
    }
    marker = request.node.get_marker('support')
    if marker:
        settings.update(marker.kwargs)

    support = WebSupport(**settings)
    yield support


with_support = pytest.mark.support


class NullStorage(StorageBackend):
    pass


@with_support(storage=NullStorage())
def test_no_srcdir(support):
    # make sure the correct exception is raised if srcdir is not given.
    with pytest.raises(RuntimeError):
        support.build()


@pytest.mark.skipif(sqlalchemy_missing, reason='needs sqlalchemy')
@with_support()
def test_build(support):
    support.build()


@pytest.mark.skipif(sqlalchemy_missing, reason='needs sqlalchemy')
@with_support()
def test_get_document(support):
    with pytest.raises(DocumentNotFoundError):
        support.get_document('nonexisting')

    contents = support.get_document('contents')
    assert contents['title'] and contents['body'] \
        and contents['sidebar'] and contents['relbar']


def test_differ():
    source = 'Lorem ipsum dolor sit amet,\nconsectetur adipisicing elit,\n' \
        'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    prop = 'Lorem dolor sit amet,\nconsectetur nihil adipisicing elit,\n' \
        'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    differ = CombinedHtmlDiff(source, prop)
    differ.make_html()
