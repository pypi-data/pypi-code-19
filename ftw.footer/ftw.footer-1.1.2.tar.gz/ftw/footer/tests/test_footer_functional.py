from ftw.footer.testing import FTW_FOOTER_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import HTTPServerError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest import TestCase
import transaction


class TestFooterFunctional(TestCase):

    layer = FTW_FOOTER_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestFooterFunctional, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        transaction.commit()

    @browsing
    def test_footer_on_non_contentish_object(self, browser):
        # This tests checks tests if the footer is rendered on non contentish
        # objects. For instance the view on an address portlet.
        browser.login().open(
            self.portal,
            {':action': "/++contextportlets++ftw.footer.column1/"
                        "+/plone.portlet.static.Static"})
        browser.fill({'Text The text to render': 'Blubber'}).submit()

        browser.open('http://nohost/plone/++contextportlets++'
                     'ftw.footer.column1/portlet_static/edit')
        self.assertEqual(
            'Blubber',
            browser.css('#footer-column-1 .portletItem').first.text)
