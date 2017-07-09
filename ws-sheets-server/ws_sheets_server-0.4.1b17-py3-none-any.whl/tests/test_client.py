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

class TestClient:
    
    def setUp(self):
        self.p1 = subprocess.Popen(('ws_storage', 'runserver', 'ws_storage.tests.conf.simple', '-d',
            '--conf_dir', 
            os.path.join(os.environ['HOME'], 'config'),
            ))
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

        #client = ws_sheets_server.sockets.Client(port)
        
        #print(client.book_new())
    
        _, protocol = await self.loop.create_connection(
            functools.partial(ws_sheets_server.client_aio.BookProtocol, self.loop),
            'localhost', 
            conf.PORT)
    
        print(protocol)
        
        await protocol.request_new()

        res = await protocol.request_sheet_data('0')
    
        print('future result')
        print(repr(res))
    

    
    
    
    
