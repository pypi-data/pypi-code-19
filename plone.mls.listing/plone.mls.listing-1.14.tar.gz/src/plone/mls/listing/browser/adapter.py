# -*- coding: utf-8 -*-
"""View adapter."""

# plone imports
from z3c.form.widget import StaticWidgetAttribute

# local imports
from plone.mls.listing import browser
from plone.mls.listing.i18n import _

LABEL_ALL = _(u'All')


PleaseSelectLCC = StaticWidgetAttribute(
    LABEL_ALL,
    view=browser.listing_collection.ListingCollectionConfiguration,
)
PleaseSelectLSF = StaticWidgetAttribute(
    LABEL_ALL,
    view=browser.listing_search.ListingSearchForm,
)
PleaseSelectRLC = StaticWidgetAttribute(
    LABEL_ALL,
    view=browser.recent_listings.RecentListingsConfiguration,
)


PleaseSelectState = StaticWidgetAttribute(
    LABEL_ALL,
    field=browser.listing_search.IListingSearchForm['location_state'],
)
PleaseSelectCounty = StaticWidgetAttribute(
    LABEL_ALL,
    field=browser.listing_search.IListingSearchForm['location_county'],
)
PleaseSelectDistrict = StaticWidgetAttribute(
    LABEL_ALL,
    field=browser.listing_search.IListingSearchForm['location_district'],
)
