# -*- coding: utf-8 -*-
"""Migration steps for ps.plone.mlstiles."""

# zope imports
from plone import api


PROFILE_ID = 'profile-ps.plone.mlstiles:default'


def migrate_to_1001(context):
    """Migrate from 1000 to 1001.

    * Install ps.plone.mls
    * Add featured listings tile.
    """
    setup = api.portal.get_tool(name='portal_setup')
    qi = api.portal.get_tool(name='portal_quickinstaller')

    qi.installProduct('ps.plone.mls')
    setup.runImportStepFromProfile(PROFILE_ID, 'plone.app.registry')
