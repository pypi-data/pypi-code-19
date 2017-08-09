# -*- coding: utf-8 -*-
"""Setuphandler."""
from zope.interface import implementer

from Products.CMFPlone.interfaces import INonInstallable


@implementer(INonInstallable)
class HiddenProfiles(object):
    """Hidden Profiles."""

    def getNonInstallableProfiles(self):  # noqa
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            'collective.permalink:uninstall',
        ]
