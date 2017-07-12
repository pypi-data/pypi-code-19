##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Functional Tests for Onlinehelp

"""
import os
import transaction
import unittest

from zope.site.interfaces import IRootFolder
from zope.app.file import File
from zope.app.onlinehelp.tests.test_onlinehelp import testdir
from zope.app.onlinehelp import globalhelp
from zope.app.onlinehelp.testing import OnlineHelpLayer

from webtest import TestApp

class BrowserTestCase(unittest.TestCase):

    layer = OnlineHelpLayer

    def setUp(self):
        super(BrowserTestCase, self).setUp()
        self._testapp = TestApp(self.layer.make_wsgi_app())

    def checkForBrokenLinks(self, orig_response, path, basic=None):
        response = self.publish(path, basic=basic)
        links = response.html.find_all('a')

        for link in links:
            href = link.attrs['href']
            if '++apidoc++' in href:
                # We don't install this at test time
                continue
            if href.startswith('http://dev.zope.org'):
                # Don't try to follow external links
                continue

            self.publish(href, basic=basic)

    def publish(self, path, basic=None, form=None, headers=None):
        assert basic
        self._testapp.authorization = ('Basic', tuple(basic.split(':')))
        env = {'wsgi.handleErrors': False}
        if form:
            response = self._testapp.post(path, params=form,
                                          extra_environ=env, headers=headers)
        else:
            response = self._testapp.get(path, extra_environ=env, headers=headers)

        response.getBody = lambda: response.unicode_normal_body
        response.getStatus = lambda: response.status_int
        response.getHeader = lambda n: response.headers[n]
        return response



class TestBrowser(BrowserTestCase):

    def test_contexthelp(self):
        path = os.path.join(testdir(), 'help.txt')
        globalhelp.registerHelpTopic('help', 'Help', '', path, IRootFolder)
        path = os.path.join(testdir(), 'help2.txt')
        globalhelp.registerHelpTopic('help2', 'Help2', '', path, IRootFolder,
            'contents.html')

        transaction.commit()

        response = self.publish("/+/action.html", basic='mgr:mgrpw',
                                form={
                                    'type_name': u'zope.app.content.File',
                                    'id': u'file'
                                })

        self.assertEqual(response.getStatus(), 302)

        response = self.publish('/contents.html', basic='mgr:mgrpw')

        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assertIn(
            "javascript:popup('contents.html/++help++/@@contexthelp.html",
            body)

        response = self.publish(
            '/contents.html/++help++/@@contexthelp.html', basic='mgr:mgrpw')

        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assertIn("This is another help!", body)

        response = self.publish('/index.html/++help++/@@contexthelp.html',
                                basic='mgr:mgrpw')

        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assertIn("This is a help!", body)

        response = self.publish('/file/edit.html/++help++/@@contexthelp.html',
                                basic='mgr:mgrpw')

        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assertIn(
            "Welcome to the Zope 3 Online Help System.",
            body)

        path = '/contents.html/++help++'
        response = self.publish(path, basic='mgr:mgrpw')

        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assertIn("Topics", body)

        self.checkForBrokenLinks(body, path, basic='mgr:mgrpw')

class TestZPT(unittest.TestCase):

    layer = OnlineHelpLayer

    def test_render(self):
        from zope.app.onlinehelp.browser import ZPTOnlineHelpTopicView
        from zope.publisher.browser import TestRequest
        from zope.location.interfaces import LocationError
        from zope.app.rotterdam import Rotterdam
        from zope.publisher.skinnable import applySkin

        class Context(object):
            path = os.path.join(os.path.dirname(__file__),
                                'helptopic.pt')
            title = 'title'

        request = TestRequest()
        applySkin(request, Rotterdam)

        # Normally these are used for IZPTOnlineHelpTopic objects,
        # which have a `path` attribute to a custom template file.
        # We're going to use it with `helptopic.pt`, which is a template
        # used for OnlineHelpTopic objects and won't work for us:
        zpt = ZPTOnlineHelpTopicView(Context, request)
        with self.assertRaises(LocationError) as e:
            zpt.renderTopic()
        self.assertEqual(e.exception.args[1], 'topicContent')

        # We have to assign a 'topicContent' to be able to use that template:
        zpt.topicContent = "the topic text"
        zpt.renderTopic()

class TestContextHelpView(unittest.TestCase):

    def test_idempotent(self):
        from zope.app.onlinehelp.browser import ContextHelpView
        view = ContextHelpView(None, None)
        view.topic = self

        self.assertIs(self, view.getContextHelpTopic())

    def test_without_view(self):
        from zope.app.onlinehelp.browser import ContextHelpView
        class Context(object):
            @property
            def context(self):
                return self
        context = Context()
        view = ContextHelpView(context, None)
        topic = view.getContextHelpTopic()
        self.assertIs(context, topic)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main()
