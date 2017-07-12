import os
import time
import yarl

import modconf


import ws_web_aiohttp
import ws_web_aiohttp.tests._test_setup

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class TestsBasic(ws_web_aiohttp.tests._test_setup.SeleniumTest):

    async def _test(self, loop, driver, conf):
        
        assert conf.test_key is not None

        url = yarl.URL('{}book_new/{}/'.format(self.url_root, 'test_' + self.__class__.__qualname__))

        url = url.with_query({'test_key': conf.test_key})

        print('url = {}'.format(url))

        await loop.run_in_executor(None, TestsBasic._test2, self, driver, url)

    def _test2(self, driver, url):
        driver.get(str(url))
       
        #self.google_login(driver)

        WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, 
                    '//table[@class="htCore"]')))
       
        print('hot table found')

        # test script pre
        e = driver.find_element_by_xpath(
                '//textarea[@id="script_pre"]')
        e.click()
        e.send_keys('import math\na=2+2\nprint(a)')

        e = driver.find_element_by_xpath(
                '//button[@id="button_script_pre"]')
        e.click()
        time.sleep(3)
        
        e = driver.find_element_by_xpath(
                '//textarea[@id="script_pre_output"]')
        
        text = e.get_attribute('value')

        print('script pre output')
        print(repr(e.get_attribute('id')))
        print(repr(text))

        assert (text == '4\n')
        
        # cell
        e = driver.find_element_by_xpath(
                '//table[@class="htCore"]/tbody/tr/td')

        e.click()
        e.send_keys('2+2\n')

        time.sleep(3)

        print('cell')
        print(repr(e.text))

        assert (e.text == '4')

        # cell
        e.click()
        e.send_keys('a\n')

        time.sleep(3)

        print('cell')
        print(repr(e.text))

        assert (e.text == '4')

        # test script post
        e = driver.find_element_by_xpath(
                '//textarea[@id="script_post"]')
        e.click()
        e.send_keys('print(a)')

        e = driver.find_element_by_xpath(
                '//button[@id="button_script_post"]')
        e.click()
        time.sleep(3)
    
        e = driver.find_element_by_xpath(
                '//textarea[@id="script_post_output"]')

        text = e.get_attribute('value')

        print('script post output')
        print(repr(text))

        assert (text == '4\n')



