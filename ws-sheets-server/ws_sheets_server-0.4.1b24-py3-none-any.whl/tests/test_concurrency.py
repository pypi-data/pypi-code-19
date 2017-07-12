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

conf_mod = 'ws_sheets_server.tests.conf.simple'

class TestConcurrency:

    def test(self, loop, addr_compute):
        loop.run_until_complete(self.go(loop, addr_compute))

    async def go(self, loop, addr_compute):
        conf = modconf.import_class(conf_mod, 'Conf', tuple(), {'dev': True})
        
        coro = loop.create_connection(
            functools.partial(ws_sheets_server.client_aio.BookProtocol, loop),
            addr_compute[0], 
            addr_compute[1],
            )
        
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


