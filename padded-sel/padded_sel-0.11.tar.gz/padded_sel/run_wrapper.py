import logging
import unittest
import json
from functools import wraps
from padded_sel.selenium_wrapper import Webdriver

logger = logging.getLogger(__name__)


def read_browser_config(file):
    """Decorator to load the Browser configuration from a local json file"""
    def decorator(function_to_decorate):
        @wraps(function_to_decorate)
        def wrapper(self, *args, **kwargs):
            with open(file, 'r') as fh:
                kwargs = json.loads(fh.read())
                return function_to_decorate(self, **kwargs)
        return wrapper
    return decorator


class WebdriverBaseTest(unittest.TestCase):
    """
    Base Test Class with support for creating and tearing down the browser object
    """

    @classmethod
    @read_browser_config("padded_sel.json")
    def setUpClass(cls, **kwargs):
        logger.debug(kwargs)
        cls.browser = Webdriver(**kwargs)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()

    def run(self, result=None):
        super(WebdriverBaseTest, self).run(TestResultEx(result, self))


class TestResultEx(object):

    def __init__(self, result, testcase):
        self.result = result
        self.testcase = testcase

    def __getattr__(self, name):
        return object.__getattribute__(self.result, name)

    def _save_screenshot(self):
        """ Check if screenshot directory exists, create it if necessary, then save screenshot, as required """
        self.testcase.browser.get_screenshot(screenshot_filename_appender=self.testcase._testMethodName)

    def addError(self, test, err):
        self.result.addError(test, err)
        self._save_screenshot()

    def addFailure(self, test, err):
        self.result.addFailure(test, err)
        self._save_screenshot()
