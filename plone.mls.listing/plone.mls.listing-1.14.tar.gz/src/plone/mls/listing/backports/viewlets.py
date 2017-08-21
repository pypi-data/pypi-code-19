# -*- coding: utf-8 -*-
"""Customized plone viewlets."""

# zope imports
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.layout.viewlets import common

# local imports
from plone.mls.listing.browser.interfaces import IListingDetails
from plone.mls.listing.backports import utils


class DublinCoreViewlet(common.DublinCoreViewlet):
    """Customized DublinCore descriptions for MLS embeddings."""

    def _get_dc_tags(self):
        """Generate the Dublin Core meta tags for an embedded item."""
        dc = {}

        if IListingDetails.providedBy(self.view):
            dc['DC.date.modified'] = self.view.data.get('modified')
            dc['DC.date.created'] = self.view.data.get('created')
            dc['DC.creator'] = self._get_mls_creator()
            dc['DC.type'] = u'MLS Listing'

        return dc

    def _get_mls_creator(self):
        """Get the creator/author from an embedded item."""

        if IListingDetails.providedBy(self.view):
            try:
                contact = self.view.contact
            except AttributeError:
                return
            else:
                return contact.get('agency', {}).get('name', {}).get('value')

    def _get_mls_description(self):
        """Get the description from an embedded item."""
        description = None

        if IListingDetails.providedBy(self.view):
            try:
                description = self.view.description
            except AttributeError:
                return

        description = utils.smart_truncate(description)
        return description

    @property
    def available(self):
        """Check if the preconditions are fullfilled."""
        return IListingDetails.providedBy(self.view)

    def update(self):
        super(DublinCoreViewlet, self).update()

        if not self.available:
            return

        try:
            use_all = api.portal.get_registry_record(
                'plone.exposeDCMetaTags'
            )
        except InvalidParameterError:
            try:
                props = api.portal.get_tool(name='portal_properties')
                use_all = props.site_properties.exposeDCMetaTags
            except Exception:
                use_all = False

        meta_dict = dict(self.metatags)
        description = self._get_mls_description()

        if use_all:
            meta_dict['DC.description'] = description
            meta_dict.update(self._get_dc_tags())
        else:
            meta_dict['description'] = description

        self.metatags = meta_dict.items()


class TitleViewlet(common.TitleViewlet):
    """Customized title Viewlet for MLS embeddings."""

    def update(self):
        super(TitleViewlet, self).update()

        title = None
        if IListingDetails.providedBy(self.view):
            try:
                title = self.view.title
            except AttributeError:
                title = getattr(self.request, 'listing_id', None)

        if title is not None:
            self.site_title = u'{0} &mdash; {1}'.format(title, self.site_title)
