import logging

from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, NoSuchAttributeException

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(module)s] [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


class Webdriver:
    def __init__(self, browser_name='firefox', platform='linux', server_url='127.0.0.1', server_port=4444, proxy=None,
                 window_size=None, persist_cookies=None):
        """
        Initialise the Webdriver and return the class object, as per the provided requirements:
        :param browser_name: String - Browser required (e.g. firefox)
        :param platform: String - OS required (e.g. linux)
        :param server_url: String - IP/DNS of the Selenium server to start the browser on
        :param server_port: Int - Port number of the Selenium server to start the browser on
        :param proxy: String - The IP/DNS and port (: separated) of a proxy server to forward traffic through
        :param window_size: String - Desired dimensions of the browser window width by height separated by 'x'
            (e.g. "1900x1200")
        :param persist_cookies: Boolean - Set to True to prevent deletion of existing cookies at startup of browser
        """
        self.capabilities = {'browserName': browser_name.lower(), 'platform': platform.upper()}
        self.command_executor = "http://{}:{}/wd/hub".format(server_url, server_port)
        self.window_size = window_size
        self.proxy = proxy
        if self.proxy:
            self.proxy = Proxy(
                {'proxyType': ProxyType.MANUAL, 'httpProxy': proxy, 'ftpProxy': proxy, 'sslProxy': proxy}
            )
            logger.debug('Browser is set to use a proxy server at {}'.format(self.proxy))
        # self.driver = webdriver.Remote(desired_capabilities=self.capabilities, command_executor=self.command_executor,
        #                                proxy=proxy)
        self.driver = webdriver.Firefox()
        logger.info('Browser initialised successfully')
        if not persist_cookies:
            self.delete_all_cookies()
        self.set_window_size(self.window_size)

    def quit(self):
        """
        Quit and close the running browser
        """
        self.driver.quit()

    def delete_all_cookies(self):
        """
        Remove all cookies from the running browser session
        """
        self.driver.delete_all_cookies()
        logger.debug('All cookies have been deleted from the new browser')

    def set_window_size(self, window_size=None):
        """
        Change the size/resolution of the browser window, defaults to 'maximum'
        :param window_size: String - Desired dimensions of the browser window width by height separated by 'x'
            (e.g. "1900x1200")
        """
        if window_size:
            browser_resolution = window_size.split("x")
            self.driver.set_window_size(int(browser_resolution[0]), int(browser_resolution[1]))
            logger.info('Browser re-sized to {}'.format(window_size))
        else:
            self.driver.set_window_size(800, 600)
            logger.info("Browser window set to default '800x600'")

    def goto(self, url):
        """
        Go to a specific URL
        """
        logger.debug("Navigating to new URL: {}".format(url))
        self.driver.get(url)
        logger.info("New window location is: {}".format(self.driver.current_url))

    def get_window_location(self):
        """
        Return the current window location (URL)
        :return: String
        """
        logger.debug("Current URL: {}".format(self.driver.current_url))
        return self.driver.current_url

    def get_window_title(self):
        """
        Return the current window's title
        :return: String
        """
        logger.debug("Current window title: {}".format(self.driver.title))
        return self.driver.title

    @staticmethod
    def pause(seconds):
        """
        Pause execution for the given number of seconds
        :param seconds: Int - Number of seconds (or part seconds)
        """
        from time import sleep
        sleep(float(seconds))
        logger.debug("Paused for {} seconds. Continuing...".format(seconds))

    def switch_to_window(self, window_name):
        """
        Switches focus to the specified window.
        :param window_name: The name or window handle of the window to switch to.
        """
        self.driver.switch_to.window(window_name)

    def switch_to_iframe(self, frame_reference):
        """
        Switch focus to the specified iframe
        :param frame_reference: The name of the window to switch to, an integer representing the index, or a webelement
                                that is an (i)frame to switch to.
        """
        self.driver.switch_to.frame(frame_reference)

    def switch_to_default_frame(self):
        """
        Switch focus to the default frame.
        """
        self.driver.switch_to.default_content()

    def switch_to_alert(self):
        """
        Switch to an alert on the page, return the Alert object
        :return: Alert object
        """
        return self.driver.switch_to.alert()

    def is_text_present_on_page(self, text):
        """
        Search for the presence of text on he current page
        :param text: String - The text to search for
        :return: Boolean
        """
        if text in self.driver.find_element_by_css_selector('BODY').text:
            logger.debug("Test '{}' IS present on the page".format(text))
            return True
        logger.debug("Test '{}' is NOT present on the page".format(text))
        return False

    def get_active_element(self):
        """
        Returns the element with focus, or BODY if nothing has focus.
        :return: WebElement object which currently has focus
        """
        return self.driver.switch_to.active_element

    def send_keys_by_id(self, element_id, text, append=False):
        """
        Send keys to an element, located by it's 'id' attribute
        :param element_id: String - the attribute value
        :param text: String - the text to send into the located element
        :param append: Boolean - If False then the element will have any existing text deleted first
        """
        if not append:
            self.clear_content_by_id(element_id)
        self.driver.find_element_by_id(element_id).send_keys(text)
        logger.debug("The phrase '{}' was sent to id={}".format(text, element_id))

    def send_keys_by_name(self, element_name, text, append=False):
        """
        Send keys to an element, located by it's 'name' attribute
        :param element_name: String - the attribute value
        :param text: String - the text to send into the located element
        :param append: Boolean - If False then the element will have any existing text deleted first
        """
        if not append:
            self.clear_content_by_name(element_name)
        self.driver.find_element_by_name(element_name).send_keys(text)
        logger.debug("The phrase '{}' was sent to name={}".format(text, element_name))

    def send_keys_by_xpath(self, element_xpath, text, append=False):
        """
        Send keys to an element, located by it's xpath
        :param element_xpath: String - the attribute value
        :param text: String - the text to send into the located element
        :param append: Boolean - If False then the element will have any existing text deleted first
        """
        if not append:
            self.clear_content_by_xpath(element_xpath)
        self.driver.find_element_by_xpath(element_xpath).send_keys(text)
        logger.debug("The phrase '{}' was sent to {}".format(text, element_xpath))

    def send_keys_by_css(self, element_css, text, append=False):
        """
        Send keys to an element, located by it's xpath
        :param element_css: String - the css value
        :param text: String - the text to send into the located element
        :param append: Boolean - If False then the element will have any existing text deleted first
        """
        if not append:
            self.clear_content_by_xpath(element_css)
        self.driver.find_element_by_css_selector(element_css).send_keys(text)
        logger.debug("The phrase '{}' was sent to (CSS) '{}'".format(text, element_css))

    def send_keys_to_active_tinymce_widget(self, text):
        """
        Enter text into a *selected* TinyMCE (type of WYSIWYG text entry field).
        :param text: String - The text you wish to enter into the field
        """
        self.driver.execute_script("tinyMCE.activeEditor.selection.setContent('{}')".format(text))

    def clear_content_by_id(self, element_id):
        """
        Remove the text from an element based on it's 'id' attribute
        :param element_id: String - the attribute value
        """
        self.driver.find_element_by_id(element_id).clear()
        logger.debug("Any existing text has been deleted from id={}".format(element_id))

    def clear_content_by_name(self, element_name):
        """
        Remove the text from an element based on it's 'name' attribute
        :param element_name: String - the attribute value
        """
        self.driver.find_element_by_name(element_name).clear()
        logger.debug("Any existing text has been deleted from name={}".format(element_name))

    def clear_content_by_xpath(self, element_xpath):
        """
        Remove the text from an element based on it's xpath
        :param element_xpath: String - the xpath value
        """
        self.driver.find_element_by_name(element_xpath).clear()
        logger.debug("Any existing text has been deleted from {}".format(element_xpath))

    def clear_content_by_css(self, element_css):
        """
        Remove the text from an element based on it's CSS
        :param element_css: String - the CSS value
        """
        self.driver.find_element_by_name(element_css).clear()
        logger.debug("Any existing text has been deleted from (CSS) '{}'".format(element_css))

    def get_text_by_id(self, element_id):
        """
        Return the text of an element based on it's 'id' attribute
        :param element_id: String - the attribute value
        :returns String: The text value of the element
        """
        text_content = self.driver.find_element_by_id(element_id).text
        logger.debug("Found text '{}' in id={}".format(text_content, element_id))
        return text_content

    def get_text_by_name(self, element_name):
        """
        Return the text of an element based on it's 'id' attribute
        :param element_name: String - the attribute value
        :returns String: The text value of the element
        """
        text_content = self.driver.find_element_by_id(element_name).text
        logger.debug("Found text '{}' in name={}".format(text_content, element_name))
        return text_content

    def get_text_by_xpath(self, element_xpath):
        """
        Return the text of an element based on it's xpath
        :param element_xpath: String - the xpath value
        :returns String: The text value of the element
        """
        text_content = self.driver.find_element_by_id(element_xpath).text
        logger.debug("Found text '{}' in name={}".format(text_content, element_xpath))
        return text_content

    def get_text_by_css(self, element_css):
        """
        Return the text of an element based on it's xpath
        :param element_css: String - the CSS value
        :returns String: The text value of the element
        """
        text_content = self.driver.find_element_by_css_selector(element_css).text
        logger.debug("Found text '{}' in name={}".format(text_content, element_css))
        return text_content

    @staticmethod
    def _get_attribute_value(element, attribute):
        """
        Look at a WebElement object and return the value of the specified attribute
        :param element: WebElement - A WebElement object
        :param attribute: String - The name of the attribute to look at
        :return: The attribute's value (string) of False is not found
        """
        try:
            return element.get_attribute(attribute)
        except NoSuchAttributeException:
            logger.warning("The attribute requested ({}) does not exist".format(attribute))
            return False

    def get_attribute_value_by_id(self, element_id, attribute):
        """
        Get the value of an attribute for an element, based on it's id
        :param element_id: String - the id of the element to look for
        :param attribute: String - the name of the attribute to look at
        :return: The attribute's value (string) of False is not found
        """
        return self._get_attribute_value(self.driver.find_element_by_id(element_id), attribute)

    def get_attribute_value_by_xpath(self, xpath, attribute):
        """
        Get the value of an attribute for an element, based on it's id
        :param xpath: String - the xpath of the element to look for
        :param attribute: String - the name of the attribute to look at
        :return: The attribute's value (string) of False is not found
        """
        return self._get_attribute_value(self.driver.find_element_by_xpath(xpath), attribute)

    def get_attribute_value_by_name(self, element_name, attribute):
        """
        Get the value of an attribute for an element, based on it's id
        :param element_name: String - the name of the element to look for
        :param attribute: String - the name of the attribute to look at
        :return: The attribute's value (string) of False is not found
        """
        return self._get_attribute_value(self.driver.find_element_by_name(element_name), attribute)

    def get_attribute_value_by_css(self, element_css, attribute):
        """
        Get the value of an attribute for an element, based on it's id
        :param element_css: String - the CSS of the element to look for
        :param attribute: String - the name of the attribute to look at
        :return: The attribute's value (string) of False is not found
        """
        return self._get_attribute_value(self.driver.find_element_by_css_selector(element_css), attribute)

    def get_attribute_value_by_link_text(self, link_text, attribute):
        """
        Get the value of an attribute for an element, based on it's id
        :param link_text: String - the link text of the element to look for
        :param attribute: String - the name of the attribute to look at
        :return: The attribute's value (string) of False is not found
        """
        return self._get_attribute_value(self.driver.find_element_by_link_text(link_text), attribute)

    def get_attribute_value_by_partial_link_text(self, partial_link_text, attribute):
        """
        Get the value of an attribute for an element, based on it's id
        :param partial_link_text: String - the partial link text of the element to look for
        :param attribute: String - the name of the attribute to look at
        :return: The attribute's value (string) of False is not found
        """
        return self._get_attribute_value(self.driver.find_element_by_partial_link_text(partial_link_text), attribute)

    def click_by_id(self, element_id):
        """
        Click on an element based on it's 'id' attribute
        :param element_id: String - the attribute value
        """
        self.driver.find_element_by_id(element_id).click()
        logger.debug("Clicked id={}".format(element_id))

    def click_by_text(self, text, tag_type="*"):
        """
        Click on an element based on it's text content, optionally restrict this to a specific html tag type
        :param text: String - text to click on
        :param tag_type: String - (optional) specific the type of html tag to click on
        """
        if text == "":
            raise ValueError("'text' cannot be blank")
        xpath = '//{}[contains(text(),"{}")]'.format(tag_type, text)
        self.click_by_xpath(xpath)
        logger.debug("Clicked text '{}' matching tag type '{}'".format(text, tag_type))

    def click_by_xpath(self, xpath):
        """
        Click on an element based on it's xpath
        :param xpath: String - the attribute value
        """
        self.driver.find_element_by_id(xpath).click()
        logger.debug("Clicked xpath '{}'".format(xpath))

    def click_by_css(self, element_css):
        """
        Click on an element based on it's CSS
        :param element_css: String - the CSS of the element
        """
        self.driver.find_element_by_css_selector(element_css).click()
        logger.debug("Clicked CSS '{}'".format(element_css))

    def click_by_name(self, element_name):
        """
        Click on an element based on it's 'name' attribute
        :param element_name: String - the attribute value
        """
        self.driver.find_element_by_id(element_name).click()
        logger.debug("Clicked name={}".format(element_name))

    def click_by_link_text(self, link_text):
        """
        Click on an element based on it's link text
        :param link_text: String - the link text
        """
        self.driver.find_element_by_link_text(link_text).click()
        logger.debug("Clicked link '{}'".format(link_text))

    def click_by_link_partial_link_text(self, partial_link_text):
        """
        Click on an element based on it's link text
        :param partial_link_text: String - the partial link text
        """
        self.driver.find_element_by_partial_link_text(partial_link_text).click()
        logger.debug("Clicked partial link '{}'".format(partial_link_text))

    def check_by_id(self, element_id):
        """
        Check a checkbox element based on it's id
        :param element_id: String - the attribute value
        """
        if not self.driver.find_element_by_id(element_id).is_selected():
            self.driver.find_element_by_id(element_id).click()
        logger.debug("Check box id={} is now checked".format(element_id))

    def check_by_xpath(self, xpath):
        """
        Check a checkbox element based on it's xpath
        :param xpath: String - the xpath
        """
        if not self.driver.find_element_by_xpath(xpath).is_selected():
            self.driver.find_element_by_xpath(xpath).click()
        logger.debug("Check box '{}' is now checked".format(xpath))

    def check_by_css(self, element_css):
        """
        Check a checkbox element based on it's CSS
        :param element_css: String - the CSS selector
        """
        if not self.driver.find_element_by_css_selector(element_css).is_selected():
            self.driver.find_element_by_css_selector(element_css).click()
        logger.debug("Check box (CSS) '{}' is now checked".format(element_css))

    def check_by_name(self, element_name):
        """
        Check a checkbox element based on it's name
        :param element_name: String - the name
        """
        if not self.driver.find_element_by_name(element_name).is_selected():
            self.driver.find_element_by_name(element_name).click()
        logger.debug("Check box name='{}' is now checked".format(element_name))

    def uncheck_by_id(self, element_id):
        """
        Check a checkbox element based on it's id
        :param element_id: String - the attribute value
        """
        if self.driver.find_element_by_id(element_id).is_selected():
            self.driver.find_element_by_id(element_id).click()
        logger.debug("Check box id={} is now unchecked".format(element_id))

    def uncheck_by_xpath(self, xpath):
        """
        Check a checkbox element based on it's xpath
        :param xpath: String - the xpath
        """
        if self.driver.find_element_by_xpath(xpath).is_selected():
            self.driver.find_element_by_xpath(xpath).click()
        logger.debug("Check box '{}' is now unchecked".format(xpath))

    def uncheck_by_css(self, element_css):
        """
        Check a checkbox element based on it's CSS
        :param element_css: String - the CSS selector
        """
        if self.driver.find_element_by_css_selector(element_css).is_selected():
            self.driver.find_element_by_css_selector(element_css).click()
        logger.debug("Check box (CSS) '{}' is now unchecked".format(element_css))

    def uncheck_by_name(self, element_name):
        """
        Check a checkbox element based on it's name
        :param element_name: String - the name
        """
        if self.driver.find_element_by_name(element_name).is_selected():
            self.driver.find_element_by_name(element_name).click()
        logger.debug("Check box name='{}' is now unchecked".format(element_name))

    def _move_to_element(self, element):
        """
        Perform the action chains to move the mouse cursor to the specified element object
        :param element: A webdriver element object (WebElement)
        """
        action = webdriver.ActionChains(self.driver).move_to_element(element)
        action.perform()

    def mouse_over_by_id(self, element_id):
        """
        Move the mouse cursor over an element based on it's 'id' attribute
        :param element_id: String - the attribute value
        """
        self._move_to_element(self.driver.find_element_by_id(element_id))
        logger.debug("Cursor is now hovering over id={}".format(element_id))

    def mouse_over_by_xpath(self, xpath):
        """
        Move the mouse cursor over an element based on it's xpath
        :param xpath: String - the xpath
        """
        self._move_to_element(self.driver.find_element_by_xpath(xpath))
        logger.debug("Cursor is now hovering over '{}'".format(xpath))

    def mouse_over_by_name(self, element_name):
        """
        Move the mouse cursor over an element based on it's 'name' attribute
        :param element_name: String - the attribute value
        """
        self._move_to_element(self.driver.find_element_by_name(element_name))
        logger.debug("Cursor is now hovering over name={}".format(element_name))

    def mouse_over_by_css(self, element_css):
        """
        Move the mouse cursor over an element based on it's 'id' attribute
        :param element_css: String - the attribute value
        """
        self._move_to_element(self.driver.find_element_by_css_selector(element_css))
        logger.debug("Cursor is now hovering over (CSS) '{}'".format(element_css))

    def mouse_over_by_link_text(self, link_text):
        """
        Move the mouse cursor over an element based on it's 'id' attribute
        :param link_text: String - the link text
        """
        self._move_to_element(self.driver.find_element_by_link_text(link_text))
        logger.debug("Cursor is now hovering over link '{}'".format(link_text))

    def mouse_over_by_partial_link_text(self, partial_link_text):
        """
        Move the mouse cursor over an element based on it's 'id' attribute
        :param partial_link_text: String - the partial link text
        """
        self._move_to_element(self.driver.find_element_by_partial_link_text(partial_link_text))
        logger.debug("Cursor is now hovering over partial link '{}'".format(partial_link_text))

    @staticmethod
    def _wait_for_attribute_value(element, attribute, value, timeout):
        """
        Wait for the specified element to have the specified attribute value
        :param element: A webdriver element object (WebElement)
        :param attribute: String - the name of the attribute to check
        :param value: String - the value of the attribute to wait for
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        from time import sleep
        for i in range(int(timeout)):
            try:
                if value in element.get_attribute(attribute):
                    logger.debug("{}={} is now true".format(attribute, value))
                    return True
            except NoSuchAttributeException:
                pass
            sleep(1)
        logger.warning("{}={} didn't become true within the time limit of {} seconds".format(attribute, value, timeout))
        return False

    def wait_for_attribute_value_by_id(self, element_id, attribute, value, timeout):
        """
        Wait for an element to have a specified attribute-value pairing, based on it's 'id' attribute
        :param element_id: String - the id of the element
        :param attribute: String - the name of the attribute to check
        :param value: String - the value of the attribute to wait for
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        logger.debug("Waiting for id={} to have {}={}".format(element_id, attribute, value))
        return self._wait_for_attribute_value(self.driver.find_element_by_id(element_id), attribute, value, timeout)

    def wait_for_attribute_value_by_xpath(self, xpath, attribute, value, timeout):
        """
        Wait for an element to have a specified attribute-value pairing, based on it's 'id' attribute
        :param xpath: String - the xpath
        :param attribute: String - the name of the attribute to check
        :param value: String - the value of the attribute to wait for
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        logger.debug("Waiting for '{}' to have {}={}".format(xpath, attribute, value))
        return self._wait_for_attribute_value(self.driver.find_element_by_xpath(xpath), attribute, value, timeout)

    def wait_for_attribute_value_by_name(self, element_name, attribute, value, timeout):
        """
        Wait for an element to have a specified attribute-value pairing, based on it's 'id' attribute
        :param element_name: String - the name of the element
        :param attribute: String - the name of the attribute to check
        :param value: String - the value of the attribute to wait for
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        logger.debug("Waiting for name={} to have {}={}".format(element_name, attribute, value))
        return self._wait_for_attribute_value(self.driver.find_element_by_name(element_name), attribute, value, timeout)

    def wait_for_attribute_value_by_css(self, element_css, attribute, value, timeout):
        """
        Wait for an element to have a specified attribute-value pairing, based on it's 'id' attribute
        :param element_css: String - the CSS of the element
        :param attribute: String - the name of the attribute to check
        :param value: String - the value of the attribute to wait for
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        logger.debug("Waiting for (CSS) '{}' to have {}={}".format(element_css, attribute, value))
        return self._wait_for_attribute_value(self.driver.find_element_by_css_selector(element_css), attribute, value, timeout)

    def wait_for_value_by_id(self, element_id, value, timeout):
        """
        Wait for an element to have a specified attribute-value pairing, based on it's 'id' attribute
        :param element_id: String - the id of the element
        :param value: String - the value of the attribute to wait for
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        logger.debug("Waiting for id={} to have value={}".format(element_id, value))
        return self._wait_for_attribute_value(self.driver.find_element_by_id(element_id), "value", value, timeout)

    def wait_for_value_by_xpath(self, xpath, value, timeout):
        """
        Wait for an element to have a specified attribute-value pairing, based on it's 'id' attribute
        :param xpath: String - the xpath
        :param value: String - the value of the attribute to wait for
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        logger.debug("Waiting for '{}' to have value={}".format(xpath, value))
        return self._wait_for_attribute_value(self.driver.find_element_by_xpath(xpath), "value", value, timeout)

    def wait_for_value_by_name(self, element_name, value, timeout):
        """
        Wait for an element to have a specified attribute-value pairing, based on it's 'id' attribute
        :param element_name: String - the name of the element
        :param value: String - the value of the attribute to wait for
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        logger.debug("Waiting for name={} to have value={}".format(element_name, value))
        return self._wait_for_attribute_value(self.driver.find_element_by_name(element_name), "value", value, timeout)

    def wait_for_value_by_css(self, element_css, value, timeout):
        """
        Wait for an element to have a specified attribute-value pairing, based on it's 'id' attribute
        :param element_css: String - the CSS of the element
        :param value: String - the value of the attribute to wait for
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        logger.debug("Waiting for (CSS) '{}' to have value={}".format(element_css, value))
        return self._wait_for_attribute_value(self.driver.find_element_by_css_selector(element_css), "value", value, timeout)

    def _is_element_present(self, identifier_type, identifier_value):
        """
        Assert the presence (or lack thereof) of a specified WebElement object
        :param identifier_type: String - A selenium "By" object
        :param identifier_value: The value of the identifier to look for
        :return: Boolean
        """
        try:
            self.driver.find_element(identifier_type, identifier_value)
            logger.debug("Element {}={} found".format(identifier_type, identifier_value))
            return True
        except NoSuchElementException:
            return False

    def is_element_present_by_id(self, element_id):
        """
        Assert whether or not an element is present on the page
        :param element_id: String - The id of the element to look for
        :return: Boolean
        """
        return self._is_element_present(By.ID, element_id)

    def is_element_present_by_xpath(self, xpath):
        """
        Assert whether or not an element is present on the page
        :param xpath: String - The xpath of the element to look for
        :return: Boolean
        """
        return self._is_element_present(By.XPATH, xpath)

    def is_element_present_by_link_text(self, link_text):
        """
        Assert whether or not an element is present on the page
        :param link_text: String - The link text of the element to look for
        :return: Boolean
        """
        return self._is_element_present(By.LINK_TEXT, link_text)

    def is_element_present_by_partial_link_text(self, partial_link_text):
        """
        Assert whether or not an element is present on the page
        :param partial_link_text: String - The partial link text of the element to look for
        :return: Boolean
        """
        return self._is_element_present(By.PARTIAL_LINK_TEXT, partial_link_text)

    def is_element_present_by_name(self, element_name):
        """
        Assert whether or not an element is present on the page
        :param element_name: String - The name of the element to look for
        :return: Boolean
        """
        return self._is_element_present(By.NAME, element_name)

    def is_element_present_by_css(self, element_css):
        """
        Assert whether or not an element is present on the page
        :param element_css: String - The CSS of the element to look for
        :return: Boolean
        """
        return self._is_element_present(By.CSS_SELECTOR, element_css)

    def _wait_for_element_present(self, identifier_type, identifier_value, timeout):
        """
        Wait for an element to have a specified attribute-value pairing, based on it's 'id' attribute
        :param identifier_type: String - A selenium "By" object
        :param identifier_value: The value of the identifier to look for
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        logger.debug("Waiting for element {}={} to be present".format(identifier_type, identifier_value))
        from time import sleep
        for i in range(int(timeout)):
            if self._is_element_present(identifier_type, identifier_value):
                return True
            sleep(1)
        logger.warning("Element {}={} was not found within the timeout ({} seconds)".format(identifier_type, identifier_value, timeout))
        return False

    def wait_for_element_present_by_id(self, element_id, timeout=10):
        """
        Wait for an element to be present, based on it's 'id' attribute
        :param element_id: String - the id of the element
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        return self._wait_for_element_present(By.ID, element_id, timeout)

    def wait_for_element_present_by_xpath(self, xpath, timeout=10):
        """
        Wait for an element to be present, based on it's xpath
        :param xpath: String - the xpath of the element
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        return self._wait_for_element_present(By.XPATH, xpath, timeout)

    def wait_for_element_present_by_name(self, element_name, timeout=10):
        """
        Wait for an element to be present, based on it's 'name' attribute
        :param element_name: String - the name of the element
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        return self._wait_for_element_present(By.NAME, element_name, timeout)

    def wait_for_element_present_by_css(self, element_css, timeout=10):
        """
        Wait for an element to be present, based on it's CSS
        :param element_css: String - the CSS of the element
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        return self._wait_for_element_present(By.CSS_SELECTOR, element_css, timeout)

    def wait_for_element_present_by_link_text(self, link_text, timeout=10):
        """
        Wait for an element to be present, based on it's CSS
        :param link_text: String - the link text of the element
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        return self._wait_for_element_present(By.LINK_TEXT, link_text, timeout)

    def wait_for_element_present_by_partial_link_text(self, partial_link_text, timeout=10):
        """
        Wait for an element to be present, based on it's CSS
        :param partial_link_text: String - the partial link text of the element
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        return self._wait_for_element_present(By.LINK_TEXT, partial_link_text, timeout)

    def _wait_for_element_not_present(self, identifier_type, identifier_value, timeout):
        """
        Wait for an element to have a specified attribute-value pairing, based on it's 'id' attribute
        :param identifier_type: A selenium "By" object
        :param identifier_value: The value of the identifier to look for
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        logger.debug("Waiting for element {}={} to disappear".format(identifier_type, identifier_value))
        from time import sleep
        for i in range(int(timeout)):
            try:
                self.driver.find_element_by_id()
            except NoSuchElementException:
                logger.debug("Element {}={} no longer present".format(identifier_type, identifier_value))
                return True
            sleep(1)
        logger.warning("Element {}={} was present for the entire timeout ({} seconds)".format(identifier_type, identifier_value, timeout))
        return False

    def wait_for_element_not_present_by_id(self, element_id, timeout=10):
        """
        Wait for an element to be present, based on it's 'id' attribute
        :param element_id: String - the id of the element
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        return self._wait_for_element_present(By.ID, element_id, timeout)

    def wait_for_element_not_present_by_xpath(self, xpath, timeout=10):
        """
        Wait for an element to be present, based on it's xpath
        :param xpath: String - the xpath of the element
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        return self._wait_for_element_not_present(By.XPATH, xpath, timeout)

    def wait_for_element_not_present_by_name(self, element_name, timeout=10):
        """
        Wait for an element to be present, based on it's 'name' attribute
        :param element_name: String - the name of the element
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        return self._wait_for_element_not_present(By.NAME, element_name, timeout)

    def wait_for_element_not_present_by_css(self, element_css, timeout=10):
        """
        Wait for an element to be present, based on it's CSS
        :param element_css: String - the CSS of the element
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        return self._wait_for_element_not_present(By.CSS_SELECTOR, element_css, timeout)

    def wait_for_element_not_present_by_link_text(self, link_text, timeout=10):
        """
        Wait for an element to be present, based on it's CSS
        :param link_text: String - the link text of the element
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        return self._wait_for_element_not_present(By.LINK_TEXT, link_text, timeout)

    def wait_for_element_not_present_by_partial_link_text(self, partial_link_text, timeout=10):
        """
        Wait for an element to be present, based on it's CSS
        :param partial_link_text: String - the partial link text of the element
        :param timeout: Int - The maximum amount of time to wait for the attribute (seconds)
        """
        return self._wait_for_element_not_present(By.LINK_TEXT, partial_link_text, timeout)

    def _is_element_visible(self, identifier_type, identifier_value):
        """
        Identify whether or not an element is currently visible within the browser window
        :param identifier_type: A selenium "By" object
        :param identifier_value: The value of the identifier to look for
        :return: Boolean - True for element is displayed, False if not
        """
        try:
            if self.driver.find_element(identifier_type, identifier_value).is_displayed():
                logger.debug("Element {}={} is now visible on the screen".format(identifier_type, identifier_value))
                return True
            logger.debug("Element {}={} is not visible on the screen".format(identifier_type, identifier_value))
        except NoSuchElementException:
            logger.warning("Element {}={} cannot be found!".format(identifier_type, identifier_value))
            return False

    def is_element_visible_by_id(self, element_id):
        """
        Check if the specified element is visible on the screen
        :param element_id: String id of the element to look for
        :return:
        """
        return self._is_element_visible(By.ID, element_id)

    def is_element_visible_by_xpath(self, xpath):
        """
        Check if the specified element is visible on the screen
        :param xpath: String xpath of the element to look for
        :return:
        """
        return self._is_element_visible(By.XPATH, xpath)

    def is_element_visible_by_link_text(self, link_text):
        """
        Check if the specified element is visible on the screen
        :param link_text: String link text of the element to look for
        :return:
        """
        return self._is_element_visible(By.LINK_TEXT, link_text)

    def is_element_visible_by_partial_link_text(self, partial_link_text):
        """
        Check if the specified element is visible on the screen
        :param partial_link_text: String partial link text of the element to look for
        :return:
        """
        return self._is_element_visible(By.PARTIAL_LINK_TEXT, partial_link_text)

    def is_element_visible_by_name(self, element_name):
        """
        Check if the specified element is visible on the screen
        :param element_name: String name of the element to look for
        :return:
        """
        return self._is_element_visible(By.NAME, element_name)

    def is_element_visible_by_css(self, element_css):
        """
        Check if the specified element is visible on the screen
        :param element_css: String CSS of the element to look for
        :return:
        """
        return self._is_element_visible(By.CSS_SELECTOR, element_css)

    def _scroll_down_to_element(self, identifier_type, identifier_value):
        """
        Scroll down to until a specified element is displayed on the screen
        :param identifier_type: A selenium "By" object
        :param identifier_value: The value of the identifier to look for
        """
        while not browser.driver.execute_script("if((window.innerHeight+window.scrollY)>=document.body.offsetHeight)"
                                                "{return true;}else{return false}"):
            # While the browser is NOT scrolled to the bottom of the page
            if self._is_element_visible(identifier_type, identifier_value):
                return True
            self.driver.execute_script("window.scrollTo(0, window.innerHeight);")
        logger.warning("The page has been scrolled to the bottom, but the element {}={} was never "
                       "visible".format(identifier_type, identifier_value))
        return False

    def scroll_down_to_element_by_id(self, element_id):
        """
        Scroll down to an element with
        :param element_id: String - the id of the element to scroll down to
        """
        return self._scroll_down_to_element(By.ID, element_id)

    def scroll_down_to_element_by_xpath(self, xpath):
        """
        Scroll down to an element with
        :param xpath: String - the xpath of the element to scroll down to
        """
        return self._scroll_down_to_element(By.XPATH, xpath)

    def scroll_down_to_element_by_link_text(self, link_text):
        """
        Scroll down to an element with
        :param link_text: String - the link text of the element to scroll down to
        """
        return self._scroll_down_to_element(By.LINK_TEXT, link_text)

    def scroll_down_to_element_by_partial_link_text(self, partial_link_text):
        """
        Scroll down to an element with
        :param partial_link_text: String - the partial link text of the element to scroll down to
        """
        return self._scroll_down_to_element(By.ID, partial_link_text)

    def scroll_down_to_element_by_name(self, element_name):
        """
        Scroll down to an element with
        :param element_name: String - the name of the element to scroll down to
        """
        return self._scroll_down_to_element(By.ID, element_name)

    def scroll_down_to_element_by_css(self, element_css):
        """
        Scroll down to an element with
        :param element_css: String - the CSS of the element to scroll down to
        """
        return self._scroll_down_to_element(By.ID, element_css)

    def get_element_count_by_xpath(self, xpath):
        """
        Return a count of the elements which match a given xpath
        :param xpath: String
        :return: Int
        """
        logger.debug("Count of elements matching xpath '{}' is ".format(self.driver.find_elements_by_xpath(xpath)))
        return self.driver.find_elements_by_xpath(xpath)

    def get_element_count_by_css(self, css_selector):
        """
        Return a count of the elements which match a given CSS
        :param css_selector: String
        :return: Int
        """
        logger.debug("Count of elements matching CSS '{}' is ".format(self.driver.find_elements_by_css_selector(css_selector)))
        return self.driver.find_elements_by_css_selector(css_selector)

    def _is_element_selected(self, identifier_type, identifier_value):
        """
        Assert whether or not a WebElement object is 'selected'
        :param identifier_type: A selenium "By" object
        :param identifier_value: The value of the identifier to look for
        """
        logger.debug("Element {}={} selection state is '{}'".format(identifier_type, identifier_value,
                                                                    self.driver.find_element(identifier_type,
                                                                                             identifier_value).is_selected()))
        return self.driver.find_element(identifier_type, identifier_value).is_selected()

    def is_element_selected_by_id(self, element_id):
        """
        Assert whether or not an element is 'selected'/'checked'
        :param element_id: String - the id of the element to look for
        :return:
        """
        return self._is_element_selected(By.ID, element_id)

    def is_element_selected_by_xpath(self, xpath):
        """
        Assert whether or not an element is 'selected'/'checked'
        :param xpath: String - the xpath of the element to look for
        :return:
        """
        return self._is_element_selected(By.XPATH, xpath)

    def is_element_selected_by_name(self, element_name):
        """
        Assert whether or not an element is 'selected'/'checked'
        :param element_name: String - the name of the element to look for
        :return:
        """
        return self._is_element_selected(By.NAME, element_name)

    def is_element_selected_by_css(self, element_css):
        """
        Assert whether or not an element is 'selected'/'checked'
        :param element_css: String - the CSS of the element to look for
        :return:
        """
        return self._is_element_selected(By.CSS_SELECTOR, element_css)

    def _select_an_element(self, identifier_type, identifier_value):
        """
        'Select' a WebElement
        :param identifier_type: A selenium "By" object
        :param identifier_value: The value of the identifier to look for
        :return: WebElement object
        """
        return Select(self.driver.find_element(identifier_type, identifier_value))

    def _select_option_from_drop_down_using_visible_text(self, identifier_type, identifier_value, choice_text):
        """
        Select a given option from a drop down menu
        :param identifier_type: A selenium "By" object
        :param identifier_value: The value of the identifier to look for
        :param choice_text: Visible text of the required option
        """
        select = self._select_an_element(identifier_type, identifier_value)
        select.select_by_visible_text(choice_text)

    def _select_option_from_drop_down_using_value(self, identifier_type, identifier_value, choice_value):
        """
        Select a given option from a drop down menu
        :param identifier_type: A selenium "By" object
        :param identifier_value: The value of the identifier to look for
        :param choice_value: 'Value' attribute's value of the required option
        """
        select = self._select_an_element(identifier_type, identifier_value)
        select.select_by_value(choice_value)

    def _select_option_from_drop_down_using_index(self, identifier_type, identifier_value, choice_index):
        """
        Select a given option from a drop down menu
        :param identifier_type: A selenium "By" object
        :param identifier_value: The value of the identifier to look for
        :param choice_index: Index of the required option (i.e. position in the list)
        """
        select = self._select_an_element(identifier_type, identifier_value)
        select.select_by_index(choice_index)

    def select_option_from_drop_down_using_visible_text_by_id(self, element_id, choice_text):
        """
        Given the id of a drop down element, select an option from it, based on the option's visible text
        :param element_id: String - the id of the element to look for
        :param choice_text: String - the text to select from the drop down
        :return:
        """
        self._select_option_from_drop_down_using_visible_text(By.ID, element_id, choice_text)

    def select_option_from_drop_down_using_visible_text_by_xpath(self, xpath, choice_text):
        """
        Given the id of a drop down element, select an option from it, based on the option's visible text
        :param xpath: String - the xpath of the element to look for
        :param choice_text: String - the text to select from the drop down
        :return:
        """
        self._select_option_from_drop_down_using_visible_text(By.XPATH, xpath, choice_text)

    def select_option_from_drop_down_using_visible_text_by_name(self, element_name, choice_text):
        """
        Given the id of a drop down element, select an option from it, based on the option's visible text
        :param element_name: String - the name of the element to look for
        :param choice_text: String - the text to select from the drop down
        :return:
        """
        self._select_option_from_drop_down_using_visible_text(By.NAME, element_name, choice_text)

    def select_option_from_drop_down_using_visible_text_by_css(self, element_css, choice_text):
        """
        Given the id of a drop down element, select an option from it, based on the option's visible text
        :param element_css: String - the CSS of the element to look for
        :param choice_text: String - the text to select from the drop down
        :return:
        """
        self._select_option_from_drop_down_using_visible_text(By.CSS_SELECTOR, element_css, choice_text)

    def select_option_from_drop_down_using_value_by_id(self, element_id, choice_text):
        """
        Given the id of a drop down element, select an option from it, based on the option's value attribute
        :param element_id: String - the id of the element to look for
        :param choice_text: String - the text to select from the drop down
        :return:
        """
        self._select_option_from_drop_down_using_value(By.ID, element_id, choice_text)

    def select_option_from_drop_down_using_value_by_xpath(self, xpath, choice_text):
        """
        Given the id of a drop down element, select an option from it, based on the option's value attribute
        :param xpath: String - the xpath of the element to look for
        :param choice_text: String - the text to select from the drop down
        :return:
        """
        self._select_option_from_drop_down_using_value(By.XPATH, xpath, choice_text)

    def select_option_from_drop_down_using_value_by_name(self, element_name, choice_text):
        """
        Given the id of a drop down element, select an option from it, based on the option's value attribute
        :param element_name: String - the name of the element to look for
        :param choice_text: String - the text to select from the drop down
        :return:
        """
        self._select_option_from_drop_down_using_value(By.NAME, element_name, choice_text)

    def select_option_from_drop_down_using_value_by_css(self, element_css, choice_text):
        """
        Given the id of a drop down element, select an option from it, based on the option's value attribute
        :param element_css: String - the CSS of the element to look for
        :param choice_text: String - the text to select from the drop down
        :return:
        """
        self._select_option_from_drop_down_using_value(By.CSS_SELECTOR, element_css, choice_text)

    def select_option_from_drop_down_using_index_by_id(self, element_id, choice_text):
        """
        Given the id of a drop down element, select an option from it, based on the option's index
        :param element_id: String - the id of the element to look for
        :param choice_text: String - the text to select from the drop down
        :return:
        """
        self._select_option_from_drop_down_using_index(By.ID, element_id, choice_text)

    def select_option_from_drop_down_using_index_by_xpath(self, xpath, choice_text):
        """
        Given the id of a drop down element, select an option from it, based on the option's index
        :param xpath: String - the xpath of the element to look for
        :param choice_text: String - the text to select from the drop down
        :return:
        """
        self._select_option_from_drop_down_using_index(By.XPATH, xpath, choice_text)

    def select_option_from_drop_down_using_index_by_name(self, element_name, choice_text):
        """
        Given the id of a drop down element, select an option from it, based on the option's index
        :param element_name: String - the name of the element to look for
        :param choice_text: String - the text to select from the drop down
        :return:
        """
        self._select_option_from_drop_down_using_index(By.NAME, element_name, choice_text)

    def select_option_from_drop_down_using_index_by_css(self, element_css, choice_text):
        """
        Given the id of a drop down element, select an option from it, based on the option's index
        :param element_css: String - the CSS of the element to look for
        :param choice_text: String - the text to select from the drop down
        :return:
        """
        self._select_option_from_drop_down_using_index(By.CSS_SELECTOR, element_css, choice_text)
