# -*- coding: utf-8 -*-
# from zope import schema
from zope import schema
from zope.interface import Interface

from collective.permalink import msg_fact as _
from plone.theme.interfaces import IDefaultPloneLayer


class IThemeSpecific(IDefaultPloneLayer):
    """Theme Layer Marker Interface."""


class IPermalinkProvider(Interface):
    """Interface for object that can provide Permalink data."""

    def get_permalink():
        """Obtain permalink"""


class IPermalinkControlPanel(Interface):
    """Settings for collective.permalink."""

    enable_copytoclipboard = schema.Bool(
        title=_(
            u'label_enable_copytoclipboard',
            default=u'Enable "copy to clipboard"',
        ),
        description=_(
            u'help_enable_copytoclipboard',
            default=u'With this option enabled, every time you click on the '
                    u'permalink it\'s target adress will be copied to your '
                    u'clipboard.',
        ),
        default=True,
        required=False,
    )
