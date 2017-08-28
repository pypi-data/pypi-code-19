# coding: utf-8
from embeddify.embeddify import OEmbedMarkup


def test_unicode():
    assert OEmbedMarkup(u'föö', {}) == u'föö'
