# -*- coding: utf-8 -*-
from Products.Five import BrowserView

from collective.permalink.interfaces import IPermalinkControlPanel
from collective.permalink.interfaces import IPermalinkProvider
from plone.api import portal
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.memoize.view import memoize
from plone.z3cform import layout


class PermalinkUrlView(BrowserView):
    """View for showing permalink on Plone contents"""

    def __call__(self):
        return self.permalink

    @property
    @memoize
    def permalink(self):
        """Get the permalink info from the context"""
        try:
            return IPermalinkProvider(self.context).get_permalink()
        except TypeError:
            return None


class PermalinkUrlWithClipBoardJSView(BrowserView):
    """View for checking if clipboardjs is enabled."""

    def __call__(self):
        return self.is_clipboardjs_enabled

    @property
    @memoize
    def is_clipboardjs_enabled(self):
        """Get the permalink info from the context"""
        return portal.get_registry_record(
            'collective.permalink.interfaces.'
            'IPermalinkControlPanel.enable_copytoclipboard',
        )


class PermalinkControlPanelForm(RegistryEditForm):
    """A control panel for Permalink settings."""

    schema = IPermalinkControlPanel

    label = u'Permalink configuration'
    description = u''


PermalinkControlPanelView = layout.wrap_form(
    PermalinkControlPanelForm,
    ControlPanelFormWrapper,
)
