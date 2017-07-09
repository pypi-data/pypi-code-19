import os
import subprocess
import sys
import time

import pytest

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import modconf
import ws_web_aiohttp
from ws_sheets_server.tests.conftest import *

def web_friently(addr):
    if len(addr)==4:
        return '[{}]:{}'.format(addr[0], addr[1])
    elif len(addr)==2:
        return '{}:{}'.format(addr[0], addr[1])

conf_web_module = 'ws_web_aiohttp.tests.conf.simple_secure'

class SeleniumTest:

    def test(self, loop, webdriver, addr_web):
        self._loop = loop

        self.conf_web = modconf.import_class(conf_web_module, 'Conf', ('DEVELOP',))
        
        self.url_root = self.conf_web.url_root()

        self._loop.run_until_complete(self._test(loop, webdriver, self.conf_web))

    def google_login(self, driver):
        try:
            google_login = modconf.import_conf('google_login', 
                    os.path.join(os.environ['HOME'], 'config'))
        except:
            google_login = type('GoogleLogin', tuple(), {
                    'email': os.environ['GOOGLE_LOGIN_EMAIL'],
                    'password': os.environ['GOOGLE_LOGIN_PASSWORD'],
                    })

        WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, 
                    '//input[@id="identifierId"]')))
        
        e = driver.find_element_by_xpath('//input[@id="identifierId"]')
        
        print('enter username')
        e.click()
        e.send_keys(google_login.email)

        e = driver.find_element_by_xpath('//div[@id="identifierNext"]')
        e.click()
        
        WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, 
                    '//input[@name="password"]')))

        while True:
            try:
                e = driver.find_element_by_xpath('//input[@name="password"]')
                print('password', e)
                e.click()
                e.send_keys(google_login.password)
                break
            except Exception as e:
                print(e)
            time.sleep(1)

        e = driver.find_element_by_xpath('//div[@id="passwordNext"]')
        print('next', e)
        e.click()


