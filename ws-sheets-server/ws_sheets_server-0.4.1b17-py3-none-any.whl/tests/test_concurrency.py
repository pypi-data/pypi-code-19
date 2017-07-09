import argparse
import asyncio
import functools
import os
import sys
import json
import unittest
import time
import subprocess

import modconf
import async_patterns.protocol
import ws_sheets
import ws_sheets_server.client_aio

class TestConcurrency():

    def setUp(self):
        self.p1 = subprocess.Popen(('ws_storage', 'runserver', 'ws_storage.tests.conf.simple', '-d',
            '--conf_dir', os.path.join(os.environ['HOME'], 'config')))
        time.sleep(2)

        self.conf_mod = 'ws_sheets_server.tests.conf.simple'

        self.p = subprocess.Popen(('ws_sheets_server', 'runserver', self.conf_mod, '-d'))

        time.sleep(3)
        
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.p1.kill()
        self.p.kill()

        print('close loop')
        self.loop.close()

    def test(self):
        try:
            self.setUp()
            self.loop.run_until_complete(self.go())
        finally:
            self.tearDown()

    async def go(self):
        conf = modconf.import_class(self.conf_mod, 'Conf', ('DEVELOP',))

        coro = self.loop.create_connection(
            functools.partial(ws_sheets_server.client_aio.BookProtocol, self.loop),
            'localhost', 
            conf.PORT)

        print('connecting')

        transport, proto = await coro
    
        print('connected')
        
        await proto.request_new()

        res = await proto.request_sheet_data('0')

        futures = []

        for r in range(10):
            proto.set_cell('0', r, 0, 'sum(range(100))')
            
            fut = proto.request_sheet_data('0')

            futures.append(fut)
            #self.assertEqual(
            #        proto['0'][r, 0],

        print(futures)

        def func():
            done, pending = yield from asyncio.wait(futures)

            print('done =',done)
            print('pending =', pending)

            return None

        ret = asyncio.wait(futures)

        ret = await ret

        #ret = func()
        print('ret =', ret)

        print('complete')


