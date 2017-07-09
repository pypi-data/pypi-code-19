import os
import modconf
import subprocess
import time
import pytest

import ws_web_aiohttp

import selenium.webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from ws_sheets_server.tests.conftest import *

@pytest.fixture(scope="module")
def webdriver():
    print()
    print('creating webdriver')
    if "SAUCE_USERNAME" in os.environ:
        print('found sauce')

        username = os.environ["SAUCE_USERNAME"]
        access_key = os.environ["SAUCE_ACCESS_KEY"]
    
        #selenium.webdriver.DesiredCapabilities()
        capabilities = {
                'platform': os.environ.get('SEL_PLATFORM','WINDOWS'),
                'browserName': os.environ.get('SEL_BROWSER','firefox'),
                }
        if os.environ.get('TRAVIS', False):
            capabilities["tunnel-identifier"] = os.environ["TRAVIS_JOB_NUMBER"]
            capabilities["build"] = os.environ["TRAVIS_BUILD_NUMBER"]
            capabilities["tags"] = [os.environ["TRAVIS_PYTHON_VERSION"], "CI"]
            address = "localhost:4445"
        else:
            address = "ondemand.saucelabs.com:80"

        hub_url = "{}:{}@{}".format(username, access_key, address)
        scheme = 'http'
        driver = selenium.webdriver.Remote(desired_capabilities=capabilities, command_executor="{}://{}/wd/hub".format(scheme, hub_url))
    else:
        driver = selenium.webdriver.Firefox()
    
    return driver

"""
@pytest.fixture
def addr_web(loop, addr_storage):
    args = {
        'conf_mod': 'ws_web_aiohttp.tests.conf.simple',
        'port': 0,
        'addr_storage': addr_storage,
        'd': True,
        #'console': True,
        }

    coro = ws_web_aiohttp.server_aio.start(loop, args)

    addr, app = loop.run_until_complete(coro)
    
    yield addr
    
    coro = ws_web_aiohttp.server_aio.stop(loop, app)

    loop.run_until_complete(coro)
"""

conf_web_module = 'ws_web_aiohttp.tests.conf.simple_secure'

@pytest.fixture
def addr_web(loop, addr_compute):
    p_web = subprocess.Popen((
        sys.executable,
        '-m',
        'ws_web_aiohttp',
        'runserver',
        conf_web_module,
        '-d',
        '--console',
        '--addr-compute', addr_compute[0], str(addr_compute[1]),
        ))

    print('waiting for web server to start')
    time.sleep(5)
    
    yield
    
    p_web.kill()


