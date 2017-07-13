# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.pantry


class CollectivePantryLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.pantry)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.pantry:default')


COLLECTIVE_PANTRY_FIXTURE = CollectivePantryLayer()


COLLECTIVE_PANTRY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_PANTRY_FIXTURE,),
    name='CollectivePantryLayer:IntegrationTesting'
)


COLLECTIVE_PANTRY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_PANTRY_FIXTURE,),
    name='CollectivePantryLayer:FunctionalTesting'
)


COLLECTIVE_PANTRY_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_PANTRY_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectivePantryLayer:AcceptanceTesting'
)
