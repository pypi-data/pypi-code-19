# -*- coding: utf-8 -*-
from collective.restrictportlets.interfaces import ISettings
from plone import api


def getAddablePortletTypes(self):
    result = self._old_getAddablePortletTypes()
    if not result:
        return result
    if 'Manager' not in api.user.get_roles():
        try:
            restricted = api.portal.get_registry_record(
                name='restricted', interface=ISettings
            )
        except KeyError:
            # Happens after uninstall.
            restricted = None
        if restricted:
            result = [p for p in result if p.addview not in restricted]
    return result
