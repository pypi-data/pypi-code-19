# -*- coding: utf-8 -*-
"""Plone support for MLS Listings."""

# zope imports
from plone import api as ploneapi


PLONE_4 = '4' <= ploneapi.env.plone_version() < '5'
PLONE_5 = '5' <= ploneapi.env.plone_version() < '6'

PRODUCT_NAME = 'plone.mls.listing'


class AnnotationStorage(dict):
    """Custom annotation dict for MLS configurations."""

    context = None
