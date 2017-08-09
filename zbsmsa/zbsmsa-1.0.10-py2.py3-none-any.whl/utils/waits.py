"""
Written by: Ian Doarn

Waits

Used to explicitly wait for events to occur
using selenium's built in explicit and implicit waits.

"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zbsmsa.utils.constants import TIME_OUT
from selenium.webdriver.common.action_chains import ActionChains
import time


class Waits:
    """
    Waits class
    
    all methods using the explicit wait function
    from selenium have customizable time out's that
    are all defaulted at 10 by the global variable TIME_OUT
    """

    def __init__(self, selenium_driver, time_out=TIME_OUT):
        """
        :param selenium_driver: driver object
        :param time_out: how many time to retry, default @ 10
        """
        self.driver = selenium_driver
        self.time_out = time_out

    def implicit(self, _time=10):
        """
        Just simply wait
        
        :param _time: int
        :return: 
        """
        self.driver.implicitly_wait(_time)

    @staticmethod
    def _for(s):
        """
        wait for given amount of seconds
        
        :param s: seconds to wait
        :return: 
        """
        time.sleep(s)

    def chain_send_keys_to_driver(self, *args, wait_for_element=False, element=None):
        """
        Utilizes ActionChain to perform
        send keys multiple times for each give arg
        :param args: Undefined amount of keys to send
        :return: None
        """
        chain = ActionChains(self.driver)
        for arg in args:
            if not wait_for_element:
                chain.send_keys(arg).perform()
            else:
                self.to_exist(element)
                chain.send_keys(arg).perform()

    def to_exist(self, selection_input, find_by=By.CSS_SELECTOR, time_out=TIME_OUT):
        """
        Wait for element to become visible or to load
        
        :param selection_input: CSS selector 
        :param find_by: what to use to find element, default By.CSS_SELECTOR
        :param time_out: Time to wait before raising timeout exception
        :return: css selector since element exists, element object
        """
        element = WebDriverWait(self.driver, time_out).until(
            EC.presence_of_element_located((find_by, selection_input))
        )
        return selection_input, element

    def clickable(self, selection_input, find_by=By.CSS_SELECTOR, time_out=TIME_OUT):
        """
        Wait till element is clicked
        
        :param selection_input: CSS selector 
        :param find_by: what to use to find element, default By.CSS_SELECTOR
        :param time_out: Time to wait before raising timeout exception
        :return: None
        """
        element = WebDriverWait(self.driver, time_out).until(
            EC.element_to_be_clickable((find_by, selection_input))
        )
        # Click if its found
        element.click()

    def send_keys_to(self, text, selection_input, find_by=By.CSS_SELECTOR, time_out=TIME_OUT):
        """
        Wait to send input to element
        
        :param text: Text to give to element
        :param selection_input: CSS selector 
        :param find_by: what to use to find element, default By.CSS_SELECTOR
        :param time_out: Time to wait before raising timeout exception
        :return: 
        """
        element = WebDriverWait(self.driver, time_out).until(
            EC.element_to_be_clickable((find_by, selection_input))
        )
        # send input to element
        element.send_keys(text)

    def clear_input(self, selection_input, find_by=By.CSS_SELECTOR, time_out=TIME_OUT):
        """
        Wait to clear element of current input
        
        :param selection_input: CSS selector 
        :param find_by: what to use to find element, default By.CSS_SELECTOR
        :param time_out: Time to wait before raising timeout exception
        :return: 
        """
        element = WebDriverWait(self.driver, time_out).until(
            EC.element_to_be_clickable((find_by, selection_input))
        )
        # Clear elements current values
        element.clear()
