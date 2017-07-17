import os
import time

import pytest
import yarl

import modconf

import ws_web_aiohttp
import ws_web_aiohttp.tests._test_setup

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

@pytest.mark.asyncio
async def test(event_loop, webdriver, web):
    
    #addr_web, conf_web = addr_web
    web_app, web_uris = web

    #self.conf_web = modconf.import_class(ws_web_aiohttp.tests.conftest.conf_web_module, 'Conf', tuple(), {'dev': True})
    
    url_root = web_app['conf'].url_root()
    
    #coro = self._test(loop, webdriver, conf_web)
    #async def _test(self, loop, driver, conf):
    
    assert web_app['conf'].test_key is not None

    url = yarl.URL('{}book_new/{}/'.format(url_root, 'test_basic'))

    url = url.with_query({'test_key': web_app['conf'].test_key})

    print('url = {}'.format(url))

    await event_loop.run_in_executor(None, _test, webdriver, url)

    print('executor test complete')

def _test(webdriver, url):
    webdriver.get(str(url))
   
    WebDriverWait(webdriver, 5).until(
            EC.presence_of_element_located((By.XPATH, 
                '//table[@class="htCore"]')))
   
    print('hot table found')

    # test script pre
    e = webdriver.find_element_by_xpath(
            '//textarea[@id="script_pre"]')
    e.click()
    e.send_keys('import math\na=2+2\nprint(a)')

    e = webdriver.find_element_by_xpath(
            '//button[@id="button_script_pre"]')
    e.click()
    time.sleep(3)
    
    e = webdriver.find_element_by_xpath(
            '//textarea[@id="script_pre_output"]')
    
    text = e.get_attribute('value')

    print('script pre output')
    print(repr(e.get_attribute('id')))
    print(repr(text))

    assert (text == '4\n')
    
    # cell
    e = webdriver.find_element_by_xpath(
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
    e = webdriver.find_element_by_xpath(
            '//textarea[@id="script_post"]')
    e.click()
    e.send_keys('print(a)')

    e = webdriver.find_element_by_xpath(
            '//button[@id="button_script_post"]')
    e.click()
    time.sleep(3)

    e = webdriver.find_element_by_xpath(
            '//textarea[@id="script_post_output"]')

    text = e.get_attribute('value')

    print('script post output')
    print(repr(text))

    assert (text == '4\n')

    print('test complete')

