import unittest

import yarl

import ws_sheets.tests.test_demos
import ws_web_aiohttp.tests._test_setup

class Test(ws_web_aiohttp.tests._test_setup.SeleniumTest):

    async def _test(self, loop, webdriver, _):
        for name, cls in ws_sheets.tests.test_demos.DEMOS.items():
            await self._test1(webdriver, name, cls)

    async def _test1(self, driver, name, cls):
        
        await self._loop.run_in_executor(None, Test._test2, self, driver, name, cls)

    def _test2(self, driver, name, cls):
        url = yarl.URL('{}demo/{}/'.format(self.url_root, name))
        url = url.with_query({'test_key': self.conf_web.test_key})
        
        print('url = {}'.format(url))

        driver.get(str(url))
        
        #self.google_login(driver)

        o = cls()

        o._test_selenium(driver)


