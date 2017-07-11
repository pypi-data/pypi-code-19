import binascii
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

def webdriver_local_display():
    return selenium.webdriver.Firefox()

def sauce_setup():
    username = os.environ["SAUCE_USERNAME"]
    access_key = os.environ["SAUCE_ACCESS_KEY"]
    capabilities = {
            'platform': os.environ.get('SEL_PLATFORM','WINDOWS'),
            'browserName': os.environ.get('SEL_BROWSER','firefox'),
            }

    return username, access_key, capabilities

def webdriver_local_nodisplay():
    username, access_key, capabilities = sauce_setup()
    address = "ondemand.saucelabs.com:80"
    return webdriver_remote(capabilities, address, username, access_key)

def webdriver_travis():
    username, access_key, capabilities = sauce_setup()
    capabilities["tunnel-identifier"] = os.environ["TRAVIS_JOB_NUMBER"]
    capabilities["build"] = os.environ["TRAVIS_BUILD_NUMBER"]
    capabilities["tags"] = [os.environ["TRAVIS_PYTHON_VERSION"], "CI"]
    address = "localhost:4445"
    return webdriver_remote(capabilities, address, username, access_key)

def webdriver_remote(capabilities, address, username, access_key):
    hub_url = "{}:{}@{}".format(username, access_key, address)
    scheme = 'http'
    driver = selenium.webdriver.Remote(
            desired_capabilities=capabilities, 
            command_executor="{}://{}/wd/hub".format(scheme, hub_url))
    return driver

@pytest.fixture(scope="module")
def webdriver():
    print()
    print('creating webdriver')

    if os.environ.get('TRAVIS', False):
        driver = webdriver_travis()
    elif os.environ.get('DISPLAY', False):
        driver = webdriver_local_display()
    else:
        driver = webdriver_local_nodisplay()

    yield driver

    driver.close()

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

conf_web_module = 'ws_web_aiohttp.tests.conf.simple'

@pytest.fixture
def addr_web(loop, addr_compute):
    
    test_key = binascii.hexlify(os.urandom(32)).decode()

    kwargs = {
            'test_key': test_key,
            'dev': True
            }

    conf = modconf.import_class(conf_web_module, 'Conf', tuple(), kwargs=kwargs)

    p_web = subprocess.Popen((
        sys.executable,
        '-m',
        'ws_web_aiohttp',
        'runserver',
        conf_web_module,
        '--dev',
        '--console',
        '--addr_compute', addr_compute[0], str(addr_compute[1]),
        '--test_key', test_key,
        ))
    
    print('waiting for web server to start')
    time.sleep(3)
    
    yield (None, conf)
    
    print('kill web server process')
    p_web.kill()


