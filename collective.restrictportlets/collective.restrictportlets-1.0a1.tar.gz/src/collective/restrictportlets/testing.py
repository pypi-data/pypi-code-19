# -*- coding: utf-8 -*-
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer

import collective.restrictportlets


class CollectiveRestrictportletsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.restrictportlets)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.restrictportlets:default')


COLLECTIVE_RESTRICTPORTLETS_FIXTURE = CollectiveRestrictportletsLayer()


COLLECTIVE_RESTRICTPORTLETS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_RESTRICTPORTLETS_FIXTURE,),
    name='CollectiveRestrictportletsLayer:IntegrationTesting'
)
