# -*- coding: utf-8 -*-
"""Tests for EnforceHTTPS tween."""

from __future__ import unicode_literals
from mock import Mock
from pyramid import testing

import unittest


class TestEnforceHTTPS(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()

    def tearDown(self):
        testing.tearDown()

    def test_is_https(self):
        from pyramid_force_https import EnforceHTTPS
        self.request.url = 'https://example.com/'
        handler = Mock()
        EnforceHTTPS(handler, Mock())(self.request)
        handler.assert_called_with(self.request)

    def test_redirect(self):
        from pyramid_force_https import EnforceHTTPS
        self.request.url = 'http://example.com/foo'
        handler = Mock()
        response = EnforceHTTPS(handler, Mock())(self.request)
        self.assertEqual(response.code, 302)
        self.assertEqual(response.location, 'https://example.com/foo')
        self.assertFalse(handler.called)
