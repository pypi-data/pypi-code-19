import argparse
import asyncio
import functools
import json
import os
import subprocess
import sys
import time

import modconf
import ws_sheets
import ws_sheets_server.client_aio
import async_patterns.protocol

conf_mod = 'ws_sheets_server.tests.conf.simple'

class TestClient:
    
    def test(self, loop, addr_compute):
        loop.run_until_complete(self.go(loop, addr_compute))

    async def go(self, loop, addr_compute):
    
        conf = modconf.import_class(conf_mod, 'Conf', tuple(), {'dev': True})

        #client = ws_sheets_server.sockets.Client(port)
        
        #print(client.book_new())
    
        _, protocol = await loop.create_connection(
            functools.partial(ws_sheets_server.client_aio.BookProtocol, loop),
            addr_compute[0],
            addr_compute[1],
            )
    
        print(protocol)
        
        await protocol.request_new()

        res = await protocol.request_sheet_data('0')
    
        print('future result')
        print(repr(res))
    

    
    
    
    
