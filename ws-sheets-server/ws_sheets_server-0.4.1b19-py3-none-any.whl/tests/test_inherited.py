import asyncio
import argparse
import functools
import logging
import logging.config
import os
import sys
import json
import subprocess
import time

import pytest

import modconf
import ws_sheets
import ws_sheets.tests.test_demos
import ws_sheets_server.client_aio
import async_patterns.protocol

logger = logging.getLogger(__name__)

@pytest.fixture
def client(loop, addr_compute):
    coro = loop.create_connection(
            functools.partial(ws_sheets_server.client_aio.BookProtocol, loop),
            addr_compute[0],
            addr_compute[1],
            )
    
    #print('is closed 2', self.loop.is_closed())

    _, c = loop.run_until_complete(coro)

    yield c

    print('exiting client fixture')

async def atest(client, cls):
        #for cls in ws_sheets.tests.test_demos.DEMOS.values():
        o = cls()
        
        print('------------------\n{}\n-----------------'.format(cls))
        
        await client.request_new()
        print('got new book')
        
        o.book = client
        
        print('call atest')
        await o.atest()

        # sync with server?
        resp = await client.request_sheet_data('0')
        print(resp)

        print('test complete')

@pytest.mark.parametrize("cls", ws_sheets.tests.test_demos.DEMOS.values())
def test(loop, client, cls):
    loop.run_until_complete(atest(client, cls))





