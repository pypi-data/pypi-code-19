# -*- coding: utf-8 -*-
"""Test Layer for collective.tiles.githubgist."""

# zope imports
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
    PLONE_FIXTURE,
)
from plone.testing import (
    Layer,
    z2,
)


class Fixture(PloneSandboxLayer):
    """Custom Test Layer for collective.tiles.githubgist."""

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope for testing."""
        # Load ZCML
        import plone.app.mosaic
        self.loadZCML(package=plone.app.mosaic)
        import collective.tiles.githubgist
        self.loadZCML(package=collective.tiles.githubgist)

    def setUpPloneSite(self, portal):
        """Set up a Plone site for testing."""
        self.applyProfile(portal, 'plone.app.mosaic:default')
        self.applyProfile(portal, 'collective.tiles.githubgist:default')


FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE, ),
    name='collective.tiles.githubgist:Integration',
)

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, z2.ZSERVER_FIXTURE),
    name='collective.tiles.githubgist:Functional',
)


ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, z2.ZSERVER_FIXTURE),
    name='collective.tiles.githubgist:Acceptance',
)

ROBOT_TESTING = Layer(name='collective.tiles.githubgist:Robot')
