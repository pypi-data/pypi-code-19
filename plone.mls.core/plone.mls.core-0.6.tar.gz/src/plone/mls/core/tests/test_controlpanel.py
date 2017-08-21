# -*- coding: utf-8 -*-
"""Test Control Panel for plone.mls.core."""

# python imports
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# zope imports
from plone import api
from plone.app.testing import TEST_USER_ID, logout, setRoles
from plone.registry import Registry
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

# local imports
from plone.mls.core.browser.interfaces import IMLSSpecific
from plone.mls.core.interfaces import IMLSSettings
from plone.mls.core.testing import PLONE_MLS_CORE_INTEGRATION_TESTING


class TestMLSControlPanel(unittest.TestCase):
    """Control Panel Test Case for plone.mls.core."""
    layer = PLONE_MLS_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Additional test setup."""
        self.portal = self.layer['portal']
        alsoProvides(self.portal.REQUEST, IMLSSpecific)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.registry = Registry()
        self.registry.registerInterface(IMLSSettings)

    def test_mls_controlpanel_view(self):
        """Test that the MLS configuration view is available."""
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name='mls-controlpanel')
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_mls_controlpanel_view_protected(self):
        """Test that the MLS configuration view needs authentication."""
        from AccessControl import Unauthorized
        logout()
        self.assertRaises(Unauthorized, self.portal.restrictedTraverse,
                          '@@mls-controlpanel')

    def test_mls_in_controlpanel(self):
        """Check that there is an MLS entry in the control panel."""
        controlpanel = api.portal.get_tool(name='portal_controlpanel')
        actions = [
            a.getAction(self)['id'] for a in controlpanel.listActions()
        ]
        self.assertTrue('propertyshelf_mls' in actions)
