#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for locale data.
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

import unittest

from zope.component.testlayer import ZCMLFileLayer
from zope import component

import nti.i18n.locales
from nti.i18n.locales.interfaces import ICountryAvailability

from . import skipIfNoPlone

try:
    unicode
except NameError:
    unicode = str

class TestConfiguredCountryUtility(unittest.TestCase):

    layer = ZCMLFileLayer(nti.i18n.locales, zcml_file='configure.zcml')

    def test_country_availability(self):
        availability = component.getUtility(ICountryAvailability)
        self.assertIn(u'us', availability.getAvailableCountries())
        self.assertIn(u"us", availability.getCountries())
        self.assertIn(u'us', [x[0] for x in availability.getCountryListing()] )

        self.assertIsInstance(
            availability.getCountries()[u'us'][u'name'],
            unicode)

    @skipIfNoPlone
    def test_lookup_utility_with_plone_iface(self):
        from plone.i18n.locales.interfaces import ICountryAvailability as IPlone
        from nti.i18n.locales.countries import CountryAvailability
        utility = component.getUtility(IPlone)
        self.assertIsInstance(utility, CountryAvailability)
