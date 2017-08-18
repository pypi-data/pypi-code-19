import os
import time

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver as Browser
from selenium.webdriver.common import action_chains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


class SeleniumBase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(SeleniumBase, cls).setUpClass()
        if hasattr(settings, "SELENIUM_FIREFOX_BIN"):
            if not os.path.exists(settings.SELENIUM_FIREFOX_BIN):
                raise OSError("Firefox binary '%s' missing." % (settings.SELENIUM_FIREFOX_BIN))
            firefox_binary = FirefoxBinary(settings.SELENIUM_FIREFOX_BIN)
            cls.selenium = Browser(firefox_binary=firefox_binary)
        else:
            cls.selenium = Browser()
        # cls.selenium.set_window_size(800, 640)
        cls.selenium.set_page_load_timeout(30)
        # cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumBase, cls).tearDownClass()

    def url(self, route, *args, **kwargs):
        if route.startswith("/"):
            return '%s%s' % (self.live_server_url, route)
        else:
            return '%s%s' % (self.live_server_url, reverse(route, args=args, kwargs=kwargs))

    def by_css(self, name):
        """
        Shortcut for find element by css selector.
        """
        return self.selenium.find_element_by_css_selector(name)

    def by_csss(self, name):
        """
        Shortcut for find elementS by css selector.
        """
        return self.selenium.find_elements_by_css_selector(name)

    def find_element(self, *locator):
        return self.selenium.find_element(*locator)

    def find_elements(self, *locator):
        return self.selenium.find_elements(*locator)

    def await_selector(self, name, timeout=30):
        """
        Shortcut to poll for the presence of a selector before continuing.
        """
        start = time.time()
        while len(self.by_csss(name)) == 0:
            time.sleep(0.1)
            if time.time() - start > timeout:
                raise Exception(
                    "Timeout waiting for selector %s after %s seconds." % (name, timeout)
                )


class RedirectPage:
    tag = '.selenium-test'


class CapatchaAutoTest(SeleniumBase):
    captcha_img = (By.ID, 'captcha-image')
    submit_button = 'input[type=submit]'
    error_tag = '.error'
    spans = '.captcha-image-wrapper span'
    refresh_button = (By.ID, 'captcha-refresh')

    def focus_captcha_img(self):
        elem = self.find_element(*self.captcha_img)
        action_chains.ActionChains(self.selenium).move_to_element(elem).perform()

    def focus_span(self):
        elem = self.by_css(self.spans)
        action_chains.ActionChains(self.selenium).move_to_element(elem).perform()

    def click_captcha_point(self, x, y):
        action_chains.ActionChains(self.selenium).move_by_offset(x, y).click().perform()

    def check_css_exist(self, css):
        try:
            self.by_css(css)
            return True
        except NoSuchElementException:
            return False

    def submit(self):
        elem = self.by_css(self.submit_button)
        elem.click()

    def test_span_visible_in_captcha_and_submit(self):
        self.selenium.get(self.url('index'))
        self.focus_captcha_img()
        self.click_captcha_point(10, 10)
        self.by_css(self.spans).is_displayed()
        time.sleep(2)
        self.submit()
        self.assertTrue(self.check_css_exist(self.error_tag))
        time.sleep(2)

    def test_refresh_captcha(self):
        self.selenium.get(self.url('index'))
        self.focus_captcha_img()
        self.click_captcha_point(10, 10)
        time.sleep(2)
        self.find_element(*self.refresh_button).click()
        self.assertFalse(self.check_css_exist(self.spans))
        self.focus_captcha_img()
        self.click_captcha_point(10, 10)
        time.sleep(2)
        self.assertTrue(self.check_css_exist(self.spans))
        self.focus_span()
        time.sleep(3)
        self.by_css(self.spans).click()
        time.sleep(2)
        self.assertFalse(self.check_css_exist(self.spans))

    def test_valid_captcha(self):
        self.selenium.get(self.url('index'))
        self.focus_captcha_img()
        self.click_captcha_point(-50, 10)
        self.click_captcha_point(-30, 10)
        time.sleep(2)
        self.submit()
        self.assertTrue(self.check_css_exist(RedirectPage.tag))
        self.assertEqual('/next', reverse('next'))
        time.sleep(2)
