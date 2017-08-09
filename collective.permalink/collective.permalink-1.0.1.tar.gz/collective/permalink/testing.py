# -*- coding: utf-8 -*-
"""Testing collective.permalink."""
import collective.permalink
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile


class CollectivePermalinkLayer(PloneSandboxLayer):
    """Testing Layer for collective.permalink."""

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):  # noqa
        """Setting up the Zope Server."""
        self.loadZCML(package=collective.permalink)

    def setUpPloneSite(self, portal):  # noqa
        """Setting up Plone Site."""
        applyProfile(portal, 'collective.permalink:default')


COLLECTIVE_PERMALINK_FIXTURE = \
    CollectivePermalinkLayer()


COLLECTIVE_PERMALINK_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_PERMALINK_FIXTURE,),
    name='CollectivePermalink UnitLayer:IntegrationTesting',
)


COLLECTIVE_PERMALINK_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_PERMALINK_FIXTURE,),
    name='CollectivePermalink UnitLayer:FunctionalTesting',
)
