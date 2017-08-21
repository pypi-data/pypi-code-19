# -*- coding: utf-8 -*-
"""Setup handlers for plone.mls.listing."""

# zope imports
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            'plone.mls.listing:uninstall',
        ]
