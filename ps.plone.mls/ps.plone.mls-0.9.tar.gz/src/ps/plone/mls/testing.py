# -*- coding: utf-8 -*-
"""Test Layer for ps.plone.mls."""

# python imports
import pkg_resources

# zope imports
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
    PLONE_FIXTURE,
)
from plone.testing import Layer, z2


try:
    pkg_resources.get_distribution('plone.app.contenttypes')
except pkg_resources.DistributionNotFound:
    HAS_PA_CONTENTTYPES = False
else:
    HAS_PA_CONTENTTYPES = True


class Fixture(PloneSandboxLayer):
    """Custom Test Layer for ps.plone.mls."""
    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        """Set up Zope for testing."""
        # Load ZCML
        import plone.app.dexterity
        self.loadZCML(package=plone.app.dexterity)

        if HAS_PA_CONTENTTYPES:
            import plone.app.contenttypes
            self.loadZCML(package=plone.app.contenttypes)

        import ps.plone.mls
        self.loadZCML(package=ps.plone.mls)

    def setUpPloneSite(self, portal):
        """Set up a Plone site for testing."""
        super(Fixture, self).setUpPloneSite(portal)
        # Install into Plone site using portal_setup
        # self.applyProfile(portal, 'Products.CMFPlone:plone')

        # Plone 5 support
        if HAS_PA_CONTENTTYPES:
            self.applyProfile(portal, 'plone.app.contenttypes:default')

        self.applyProfile(portal, 'ps.plone.mls:default')
        self.applyProfile(portal, 'ps.plone.mls:testfixture')
        portal.portal_workflow.setDefaultChain('simple_publication_workflow')


FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE, ),
    name='ps.plone.mls:Integration',
)

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, z2.ZSERVER_FIXTURE),
    name='ps.plone.mls:Functional',
)

ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, z2.ZSERVER_FIXTURE),
    name='ps.plone.mls:Acceptance')

ROBOT_TESTING = Layer(name='ps.plone.mls:Robot')
