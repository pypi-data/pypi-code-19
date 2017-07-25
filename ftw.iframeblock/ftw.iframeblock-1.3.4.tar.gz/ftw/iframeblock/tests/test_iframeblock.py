from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.iframeblock.tests import FunctionalTestCase


class TestIFrameBlock(FunctionalTestCase):

    def setUp(self):
        super(TestIFrameBlock, self).setUp()
        self.grant('Manager')

    @browsing
    def test_block_url_is_parsed_to_iframe_tag_correctly(self, browser):
        """
        This test makes sure that the url passed to the creation form is added
        to the iframe tag correctly.
        """
        content_page = create(Builder('sl content page'))

        create(Builder('iframe block')
               .having(url=u'http://www.google.com')
               .within(content_page))

        browser.login().visit(content_page)

        self.assertEqual(
            u'http://www.google.com',
            browser.css('iframe.iframeblock').first.attrib['src']
        )

    @browsing
    def test_height_field_is_used_if_auto_size_is_not_set(self, browser):
        """
        Test that the height set in the block is applied to the iframe.
        """
        content_page = create(Builder('sl content page'))

        create(Builder('iframe block')
               .having(url=u'http://www.google.com')
               .having(height=u'400')
               .having(auto_size=False)
               .within(content_page))

        browser.login().visit(content_page)

        self.assertEqual(
            u'400',
            browser.css('iframe.iframeblock').first.attrib['height']
        )

    @browsing
    def test_scrolling_attribute_depending_on_auto_resize(self, browser):
        """
        The scrolling attribute has to be set to no if the iframe resizer is
        in use to avoid jittering.
        When the resizier is disabled the iframe should handle the scrollbars.
        (-> scrolling: auto)
        """
        with_resizer = create(Builder('sl content page'))
        create(Builder('iframe block')
               .having(url=u'http://www.google.com',
                       auto_size=True)
               .within(with_resizer))

        without_resizer = create(Builder('sl content page'))
        create(Builder('iframe block')
               .having(url=u'http://www.google.com',
                       auto_size=False)
               .within(without_resizer))

        browser.login().visit(with_resizer)
        self.assertEqual(
            'no',
            browser.css('iframe.iframeblock').first.attrib['scrolling']
        )

        browser.visit(without_resizer)
        self.assertEqual(
            'auto',
            browser.css('iframe.iframeblock').first.attrib['scrolling']
        )

    @browsing
    def test_alternative_url_can_be_passed_as_request_param(self, browser):
        """
        When integrating other websites in iframes and indexing those
        contents in the search, we want to be able to link from the search
        to a specific iframed sub-page.
        In order to make this possible we need to be able to pass the
        requested sub-page as GET request param.
        For security reason, the origin of both URLs must be the same,
        otherwise the configured startpage is loaded.
        """
        content_page = create(Builder('sl content page'))

        block = create(Builder('iframe block')
                       .titled('the-block')
                       .having(url=u'http://mypage.com/index.php')
                       .within(content_page))

        browser.login().visit(content_page)
        self.assertEqual(
            u'http://mypage.com/index.php',
            browser.css('iframe.iframeblock').first.attrib['src'])

        # "i", shortcut for "iframe" is the non-specific param
        browser.visit(content_page, data={
            'i': u'http://mypage.com/contact.php'})
        self.assertEqual(
            u'http://mypage.com/contact.php',
            browser.css('iframe.iframeblock').first.attrib['src'],
            'Using "?i=<URL>" should load the passed URL.')

        # "i_<ID>" can be used for beeing more specific
        browser.visit(content_page, data={
            'i_the-block': u'http://mypage.com/contact.php'})
        self.assertEqual(
            u'http://mypage.com/contact.php',
            browser.css('iframe.iframeblock').first.attrib['src'],
            'Using "?i_<BLOCKID>=<URL>" should load the passed URL.')

        # domain must match
        browser.visit(content_page, data={
            'i': u'http://hacker.com/contact.php'})
        self.assertEqual(
            u'http://mypage.com/index.php',
            browser.css('iframe.iframeblock').first.attrib['src'],
            'Non-matching domains are not allowed.')

        # switch to https is allowed
        browser.visit(content_page, data={
            'i': u'https://mypage.com/contact.php'})
        self.assertEqual(
            u'https://mypage.com/contact.php',
            browser.css('iframe.iframeblock').first.attrib['src'],
            'Switching to HTTPS is allowed.')

        # switch to other protocols is not allowed
        browser.visit(content_page, data={
            'i': u'file://mypage.com/contact.php'})
        self.assertEqual(
            u'http://mypage.com/index.php',
            browser.css('iframe.iframeblock').first.attrib['src'],
            'Switching to file:// is not allowed.')
