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
import ws_web_aiohttp.tests.conftest

class SeleniumTest:

    def test(self, loop, webdriver, addr_web):
        addr_web, conf_web = addr_web

        self._loop = loop

        #self.conf_web = modconf.import_class(ws_web_aiohttp.tests.conftest.conf_web_module, 'Conf', tuple(), {'dev': True})
        
        self.url_root = conf_web.url_root()
        
        coro = self._test(loop, webdriver, conf_web)

        self._loop.run_until_complete(coro)

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


