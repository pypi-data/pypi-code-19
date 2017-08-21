# -*- coding: utf-8 -*-
"""Different shared utilities."""

# zope imports
from plone import api
from plone.api.exc import InvalidParameterError


def smart_truncate(content):
    """Truncate a string for some max length, but split at word boundary.

    Settings for `length` and `ellipsis` are taken from the Plone settings.
    In Plone 5 the `portal_properties` tool was removed and all settings
    have been migrated to the registry. Currently the setting for
    `ellipsis` has not yet been migrated. So we have to check for both
    settings individually.
    """
    if content is None:
        return

    try:
        length = api.portal.get_registry_record(
            'plone.search_results_description_length'
        )
    except InvalidParameterError:
        try:
            props = api.portal.get_tool(name='portal_properties')
            length = props.site_properties.search_results_description_length
        except Exception:
            length = 160

    try:
        ellipsis = api.portal.get_registry_record('plone.ellipsis')
    except InvalidParameterError:
        try:
            props = api.portal.get_tool(name='portal_properties')
            ellipsis = props.site_properties.ellipsis
        except Exception:
            ellipsis = u'...'

    if len(content) > length:
        content = content[:length].rsplit(' ', 1)[0] + ellipsis
    return content
