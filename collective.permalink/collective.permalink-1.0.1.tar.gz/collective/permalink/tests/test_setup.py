# -*- coding: utf-8 -*-
"""Setup tests for this package."""
import unittest

from collective.permalink.interfaces import IThemeSpecific
from collective.permalink.testing import \
    COLLECTIVE_PERMALINK_INTEGRATION_TESTING
from plone import api
from plone.browserlayer import utils


ACTIONS = ('permalink_without_clipboard', 'permalink_with_clipboard')


class TestSetup(unittest.TestCase):
    """Test that collective.permalink is properly installed."""

    layer = COLLECTIVE_PERMALINK_INTEGRATION_TESTING

    def setUp(self):  # noqa
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.portal_actions = api.portal.get_tool('portal_actions')

    def test_product_installed(self):
        """Test if collective.permalink is installed."""
        self.assertTrue(
            self.installer.isProductInstalled(
                'collective.permalink',
            ),
        )

    def test_browserlayer(self):
        """Test that IAddOnInstalled is registered."""
        self.assertIn(
            IThemeSpecific,
            utils.registered_layers(),
        )

    def test_document_actions(self):
        """Test that Actions are added."""
        document_actions = [
            action.id for action in
            self.portal_actions.document_actions.listActions()]
        for action in ACTIONS:
            self.assertIn(action, document_actions)

    def test_object_buttons(self):
        """Test that Actions are added."""
        object_buttons = [
            action.id for action in
            self.portal_actions.object_buttons.listActions()]
        for action in ACTIONS:
            self.assertIn(action, object_buttons)


class TestUninstall(unittest.TestCase):
    """Uninstall Routine."""

    layer = COLLECTIVE_PERMALINK_INTEGRATION_TESTING

    def setUp(self):  # noqa
        """Setting up Testcase."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.permalink'])
        self.portal_actions = api.portal.get_tool('portal_actions')

    def test_product_uninstalled(self):
        """Test if collective.permalink is cleanly uninstalled."""
        self.assertFalse(
            self.installer.isProductInstalled(
                'collective.permalink',
            ),
        )

    def test_browserlayer_uninstalled(self):
        """Test that IAddOnInstalled is removed."""
        self.assertNotIn(
            IThemeSpecific,
            utils.registered_layers(),
        )

    def test_document_actions_uninstalled(self):
        """Test that Actions are added."""
        document_actions = [
            action.id for action in
            self.portal_actions.document_actions.listActions()]
        for action in ACTIONS:
            self.assertNotIn(action, document_actions)

    def test_object_buttons_uninstalled(self):
        """Test that Actions are added."""
        object_buttons = [
            action.id for action in
            self.portal_actions.object_buttons.listActions()]
        for action in ACTIONS:
            self.assertNotIn(action, object_buttons)
