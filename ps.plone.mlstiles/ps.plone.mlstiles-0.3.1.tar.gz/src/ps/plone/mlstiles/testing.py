# -*- coding: utf-8 -*-
"""Test Layer for ps.plone.mlstiles."""

# zope imports
from collective.cover.tests.utils import create_standard_content_for_tests
from plone.app.testing import (
    IntegrationTesting,
    PloneSandboxLayer,
    PLONE_FIXTURE,
)


class PSPloneMLSTiles(PloneSandboxLayer):
    """Custom Test Layer for ps.plone.mlstiles."""
    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        """Set up Zope for testing."""
        # Load ZCML
        import ps.plone.mlstiles
        self.loadZCML(package=ps.plone.mlstiles)

    def setUpPloneSite(self, portal):
        """Set up a Plone site for testing."""
        self.applyProfile(portal, 'ps.plone.mlstiles:default')
        self.applyProfile(portal, 'collective.cover:testfixture')

        # setup test content
        create_standard_content_for_tests(portal)

        portal_workflow = portal.portal_workflow
        portal_workflow.setChainForPortalTypes(
            ['Collection'], ['simple_publication_workflow'])

        # Prevent kss validation errors in Plone 4.2
        portal_kss = getattr(portal, 'portal_kss', None)
        if portal_kss:
            kss = portal_kss.getResource('++resource++plone.app.z3cform')
            kss.setEnabled(False)


PS_PLONE_MLSTILES_FIXTURE = PSPloneMLSTiles()
PS_PLONE_MLSTILES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PS_PLONE_MLSTILES_FIXTURE, ),
    name='PSPloneMLSTiles:Integration',
)
