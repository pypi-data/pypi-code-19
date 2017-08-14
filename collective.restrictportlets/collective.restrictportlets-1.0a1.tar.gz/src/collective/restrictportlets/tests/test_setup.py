# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.restrictportlets.testing import COLLECTIVE_RESTRICTPORTLETS_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.portlets.interfaces import IPortletManager
from zope.component import getUtility

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.restrictportlets is properly installed."""

    layer = COLLECTIVE_RESTRICTPORTLETS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.restrictportlets is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.restrictportlets'))

    def test_browserlayer(self):
        """Test that ICollectiveRestrictportletsLayer is registered."""
        from collective.restrictportlets.interfaces import (
            ICollectiveRestrictportletsLayer)
        from plone.browserlayer import utils
        self.assertIn(
            ICollectiveRestrictportletsLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_RESTRICTPORTLETS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.restrictportlets'])

    def test_product_uninstalled(self):
        """Test if collective.restrictportlets is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.restrictportlets'))

    def test_browserlayer_removed(self):
        """Test that ICollectiveRestrictportletsLayer is removed."""
        from collective.restrictportlets.interfaces import \
            ICollectiveRestrictportletsLayer
        from plone.browserlayer import utils
        self.assertNotIn(
           ICollectiveRestrictportletsLayer,
           utils.registered_layers())

    def test_member_sees_all_portlets_after_uninstall(self):
        # Explicitly set roles to Member. Somehow needed on Plone 4.3.
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        manager = getUtility(IPortletManager, name='plone.leftcolumn')
        addable = manager.getAddablePortletTypes()
        add_views = [p.addview for p in addable]
        self.assertIn('portlets.News', add_views)
        self.assertIn('portlets.Classic', add_views)
        self.assertIn('portlets.Login', add_views)
        self.assertIn('plone.portlet.static.Static', add_views)
