# -*- coding: utf-8 -*-
"""Migration steps for plone.mls.listing."""

# zope imports
from plone import api


PROFILE_ID = 'profile-plone.mls.core:default'


def migrate_to_1001(context):
    """Migrate from 1000 to 1001.

    * Activate portal actions.
    * Register JS resources.
    """
    setup = api.portal.get_tool(name='portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'actions')
    setup.runImportStepFromProfile(PROFILE_ID, 'jsregistry')
