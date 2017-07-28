# -*- coding: utf-8 -*-
"""Test Setup of spirit.plone.theming."""

# python imports
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# zope imports
from plone import api
from plone.browserlayer.utils import registered_layers

# local imports
from collective.tiles.githubgist.config import PROJECT_NAME
from collective.tiles.githubgist.testing import INTEGRATION_TESTING


class TestSetup(unittest.TestCase):
    """Test that collective.tiles.githubgist is properly installed."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        """Additional test setup."""
        self.portal = self.layer['portal']

    def test_product_installed(self):
        """Validate that our product is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled(PROJECT_NAME))

    def test_addon_layer(self):
        """Validate that the browserlayer for our product is installed."""
        from collective.tiles.githubgist.interfaces import (
            ICollectiveTilesGithubgistLayer,
        )
        self.assertIn(ICollectiveTilesGithubgistLayer, registered_layers())


class TestUninstall(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        """Additional test setup."""
        self.portal = self.layer['portal']

        qi = self.portal.portal_quickinstaller
        with api.env.adopt_roles(['Manager']):
            qi.uninstallProducts(products=[PROJECT_NAME])

    def test_product_is_uninstalled(self):
        """Validate that our product is uninstalled."""
        qi = self.portal.portal_quickinstaller
        self.assertFalse(qi.isProductInstalled(PROJECT_NAME))

    def test_addon_layer_removed(self):
        """Validate that the browserlayer is removed."""
        from collective.tiles.githubgist.interfaces import (
            ICollectiveTilesGithubgistLayer,
        )
        self.assertNotIn(ICollectiveTilesGithubgistLayer, registered_layers())
