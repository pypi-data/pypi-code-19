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
    @read_browser_config("file.json")
    def setUpClass(cls, **kwargs):
        cls.driver = Webdriver(browser_name=kwargs['browser'])
        logger.debug(kwargs)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
