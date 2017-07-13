# -*- coding: utf-8 -*-
from collective.pantry.interfaces import ISnippet
from collective.pantry.testing import COLLECTIVE_PANTRY_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest


class SnippetIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_PANTRY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='Snippet')
        schema = fti.lookupSchema()
        self.assertEqual(ISnippet, schema)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='Snippet')
        self.assertTrue(fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='Snippet')
        factory = fti.factory
        obj = createObject(factory)
        self.assertTrue(ISnippet.providedBy(obj))

    def test_adding(self):
        obj = api.content.create(
            container=self.portal,
            type='Snippet',
            id='Snippet',
        )
        self.assertTrue(ISnippet.providedBy(obj))
