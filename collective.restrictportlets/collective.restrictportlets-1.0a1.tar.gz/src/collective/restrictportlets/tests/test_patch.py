# -*- coding: utf-8 -*-
from collective.restrictportlets.interfaces import ISettings
from collective.restrictportlets.interfaces import PortletTypesVocabularyFactory  # noqa
from collective.restrictportlets.testing import COLLECTIVE_RESTRICTPORTLETS_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.portlets.interfaces import IPortletManager
from zope.component import getUtility
from zope.schema.interfaces import WrongContainedType

import unittest


class TestPatch(unittest.TestCase):
    """Test that our patch works."""

    layer = COLLECTIVE_RESTRICTPORTLETS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.manager = getUtility(IPortletManager, name='plone.leftcolumn')

    def test_default_setting(self):
        self.assertEqual(
            api.portal.get_registry_record(
                name='restricted', interface=ISettings),
            ['portlets.Classic', 'portlets.Login']
        )

    def test_manager_sees_all_portlets(self):
        # Portlets should remain addable if nothing has been changed.
        # We do not check them all, because the list may be different in
        # Plone 4 and 5.
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        addable = self.manager.getAddablePortletTypes()
        add_views = [p.addview for p in addable]
        self.assertIn('portlets.News', add_views)
        self.assertIn('portlets.Classic', add_views)
        self.assertIn('portlets.Login', add_views)
        self.assertIn('plone.portlet.static.Static', add_views)

    def test_member_sees_some_portlets(self):
        # Some portlets are no longer addable for non-managers.
        # Explicitly set roles to Member. Somehow needed on Plone 4.3.
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        addable = self.manager.getAddablePortletTypes()
        add_views = [p.addview for p in addable]
        self.assertIn('portlets.News', add_views)
        self.assertNotIn('portlets.Classic', add_views)
        self.assertNotIn('portlets.Login', add_views)
        self.assertIn('plone.portlet.static.Static', add_views)

    def test_member_sees_different_portlets(self):
        # Test restricting different portlets than the default.
        api.portal.set_registry_record(
            name='restricted', value=['portlets.News'],
            interface=ISettings
        )
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        addable = self.manager.getAddablePortletTypes()
        add_views = [p.addview for p in addable]
        self.assertNotIn('portlets.News', add_views)
        self.assertIn('portlets.Classic', add_views)
        self.assertIn('portlets.Login', add_views)
        self.assertIn('plone.portlet.static.Static', add_views)


class TestVocabulary(unittest.TestCase):

    layer = COLLECTIVE_RESTRICTPORTLETS_INTEGRATION_TESTING

    def test_vocabulary_values(self):
        values = PortletTypesVocabularyFactory(context=None)
        self.assertIn('portlets.News', values)
        self.assertIn('portlets.Classic', values)
        self.assertIn('portlets.Login', values)
        self.assertIn('plone.portlet.static.Static', values)

    def test_vocabulary_unknown_portlet(self):
        with self.assertRaises(WrongContainedType):
            api.portal.set_registry_record(
                name='restricted', value=['no.such.portlet'],
                interface=ISettings
            )

    def test_vocabulary_unicode_value(self):
        with self.assertRaises(WrongContainedType):
            api.portal.set_registry_record(
                name='restricted', value=[u'plone.News'],
                interface=ISettings
            )
