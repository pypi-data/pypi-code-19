##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""OnlineHelp System.

Create the global ``OnlineHelp`` instance.

"""
__docformat__ = 'restructuredtext'

import os

from zope.component import getUtilitiesFor
from zope.interface import providedBy
from zope.proxy import ProxyBase
from zope.proxy import non_overridable
from zope.testing import cleanup

from zope.app.onlinehelp.interfaces import IOnlineHelpTopic
from zope.app.onlinehelp.onlinehelp import OnlineHelp


# Global Online Help Instance
path = os.path.join(os.path.dirname(__file__),
                      'help', 'welcome.stx')
globalhelp = OnlineHelp('Online Help', path)

class _TraversedOnlineHelpProxy(ProxyBase):
    """
    A proxy around the globalhelp object that is returned when we
    traverse through the helpNamespace.

    It adds the ``context`` attribute to the context that was traversed
    through.
    """
    __slots__ = ('context',)

    def __init__(self, context):
        self.context = context
        ProxyBase.__init__(self, globalhelp)

    @non_overridable
    def __reduce__(self, proto=None):
        raise TypeError("Not picklable")
    __reduce_ex__ = __reduce__


class helpNamespace(object):
    """ help namespace handler """

    def __init__(self, context, request=None):
        self.context = context

    def traverse(self, name, ignored):
        """
        Used to traverse to an online help topic.

        Returns a proxy for the global :class:`~.OnlineHelp` instance
        with the traversal context.
        """
        return _TraversedOnlineHelpProxy(self.context)


def getTopicFor(obj, view=None):
    """Determine topic for an object and optionally a view.

    Iterate through all directly provided Interfaces and
    see if for the interface (and view) exists a Help Topic.

    Returns the first match.

    Prepare the tests:

    >>> import os
    >>> from zope.app.onlinehelp.tests.test_onlinehelp import testdir
    >>> from zope.app.onlinehelp.tests.test_onlinehelp import I1, Dummy1, Dummy2
    >>> from zope.app.onlinehelp import tests as ztapi
    >>> from zope.component.interfaces import IFactory
    >>> from zope.component.factory import Factory
    >>> from zope.app.onlinehelp.onlinehelptopic import OnlineHelpTopic
    >>> from zope.app.onlinehelp.onlinehelptopic import RESTOnlineHelpTopic
    >>> from zope.app.onlinehelp.onlinehelptopic import STXOnlineHelpTopic
    >>> from zope.app.onlinehelp.onlinehelptopic import ZPTOnlineHelpTopic
    >>> default = Factory(OnlineHelpTopic)
    >>> rest = Factory(RESTOnlineHelpTopic)
    >>> stx = Factory(STXOnlineHelpTopic)
    >>> zpt = Factory(ZPTOnlineHelpTopic)
    >>> ztapi.provideUtility(IFactory, default, 'onlinehelp.topic.default')
    >>> ztapi.provideUtility(IFactory, rest, 'onlinehelp.topic.rest')
    >>> ztapi.provideUtility(IFactory, stx, 'onlinehelp.topic.stx')
    >>> ztapi.provideUtility(IFactory, zpt, 'onlinehelp.topic.zpt')
    >>> path = os.path.join(testdir(), 'help.txt')

    Register a help topic for the interface 'I1' and the view 'view.html'

    >>> onlinehelp = OnlineHelp('Help', path)
    >>> path = os.path.join(testdir(), 'help2.txt')
    >>> onlinehelp.registerHelpTopic('', 'help2', 'Help 2',
    ...     path, I1, 'view.html')

    The query should return it ('Dummy1' implements 'I1):

    >>> getTopicFor(Dummy1(),'view.html').title
    'Help 2'

    A query without view should not return it

    >>> getTopicFor(Dummy1()) is None
    True

    Do the registration again, but without a view:

    >>> onlinehelp = OnlineHelp('Help', path)
    >>> onlinehelp.registerHelpTopic('', 'help2', 'Help 2',
    ...     path, I1, None)
    >>> getTopicFor(Dummy1()).title
    'Help 2'

    Query with view should not match

    >>> getTopicFor(Dummy1(), 'view.html') is None
    True

    Query with an object, that does not provide 'I1' should
    also return None

    >>> getTopicFor(Dummy2()) is None
    True

    If there is a second interface also provided with the same
    view name and registered for that interface, still only the first
    topic will be found.

    >>> from zope.interface import Interface, implementer, alsoProvides
    >>> class I3(Interface):
    ...     pass
    >>> @implementer(I3)
    ... class Dummy3(object):
    ...     pass

    >>> path = os.path.join(testdir(), 'help2.txt')
    >>> onlinehelp.registerHelpTopic('a', 'help3', 'Help 3',
    ...     path, I3, None)

    >>> getTopicFor(Dummy3()).title
    'Help 3'
    >>> getTopicFor(Dummy1()).title
    'Help 2'

    >>> @implementer(I1, I3)
    ... class Dummy4(object):
    ...     pass
    >>> getTopicFor(Dummy4()).title
    'Help 2'

    >>> @implementer(I3, I1)
    ... class Dummy5(object):
    ...     pass
    >>> getTopicFor(Dummy5()).title
    'Help 3'

    """
    for interface in providedBy(obj):
        for _name, topic in getUtilitiesFor(IOnlineHelpTopic):
            if topic.interface == interface and topic.view == view:
                return topic

def _clear():
    globalhelp.__init__(globalhelp.title, globalhelp.path)


cleanup.addCleanUp(_clear)
