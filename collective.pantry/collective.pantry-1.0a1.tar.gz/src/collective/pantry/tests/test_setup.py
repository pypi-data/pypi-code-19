# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.pantry.testing import COLLECTIVE_PANTRY_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.pantry is properly installed."""

    layer = COLLECTIVE_PANTRY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.pantry is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.pantry'))

    def test_browserlayer(self):
        """Test that ICollectivePantryLayer is registered."""
        from collective.pantry.interfaces import (
            ICollectivePantryLayer)
        from plone.browserlayer import utils
        self.assertIn(
            ICollectivePantryLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_PANTRY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.pantry'])

    def test_product_uninstalled(self):
        """Test if collective.pantry is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.pantry'))

    def test_browserlayer_removed(self):
        """Test that ICollectivePantryLayer is removed."""
        from collective.pantry.interfaces import \
            ICollectivePantryLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            ICollectivePantryLayer,
            utils.registered_layers())
