from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from zope.configuration import xmlconfig


class FtwFooterLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)
        # Load ZCML
        import ftw.footer

        xmlconfig.file('configure.zcml', ftw.footer,
                       context=configurationContext)

        z2.installProduct(app, 'ftw.footer')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.footer:default')


FTW_FOOTER_FIXTURE = FtwFooterLayer()
FTW_FOOTER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_FOOTER_FIXTURE, ), name="FtwFooter:Integration")

FTW_FOOTER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_FOOTER_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="FtwFooter:Functional")
