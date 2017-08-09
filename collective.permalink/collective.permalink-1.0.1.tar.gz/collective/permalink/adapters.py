# -*- coding: utf-8 -*-
from zope.component import getUtility

from plone.api import content
from plone.api import portal
from plone.registry.interfaces import IRegistry


class UUIDAwarePermalinkAdapter(object):
    """Permalink Adapter."""

    def __init__(self, context):
        self.context = context

    def get_permalink(self):
        """Create a permalink."""
        registry = getUtility(IRegistry)
        types_use_view_action = frozenset(
            registry.get('plone.types_use_view_action_in_listings', []),
        )

        if self.context.portal_type in types_use_view_action:
            suffix = '/view'
        else:
            suffix = ''
        return '{0}/resolveuid/{1}{2}'.format(
                    portal.get().absolute_url(),
                    content.get_uuid(self.context),
                    suffix,
                )
