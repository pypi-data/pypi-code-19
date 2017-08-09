# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.app.portlets.interfaces import IColumn
    
from z3c.form import interfaces
from zope import schema
from zope.interface import alsoProvides
from plone.directives import form


class IMedialogAboveContentPortletsLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""

class IBelow(IColumn):
    """here we put the below content portlets
    """    

class IAbove(IColumn):
    """here we put the above content portlets
    """    

