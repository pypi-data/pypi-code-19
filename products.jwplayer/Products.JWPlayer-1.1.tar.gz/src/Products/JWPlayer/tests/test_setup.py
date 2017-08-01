# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from Products.JWPlayer.testing import PRODUCTS_JWPLAYER_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that Products.JWPlayer is properly installed."""

    layer = PRODUCTS_JWPLAYER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if Products.JWPlayer is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'Products.JWPlayer'))

    def test_browserlayer(self):
        """Test that IProductsJwplayerLayer is registered."""
        from Products.JWPlayer.interfaces import (
            IProductsJwplayerLayer)
        from plone.browserlayer import utils
        self.assertIn(IProductsJwplayerLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = PRODUCTS_JWPLAYER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['Products.JWPlayer'])

    def test_product_uninstalled(self):
        """Test if Products.JWPlayer is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'Products.JWPlayer'))

    def test_browserlayer_removed(self):
        """Test that IProductsJwplayerLayer is removed."""
        from Products.JWPlayer.interfaces import \
            IProductsJwplayerLayer
        from plone.browserlayer import utils
        self.assertNotIn(IProductsJwplayerLayer, utils.registered_layers())
