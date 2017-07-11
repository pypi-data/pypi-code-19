import os
import sys
import functools
import asyncio
import json
import argparse
import modconf
import subprocess
import time
import pickle
import logging.config

import pytest

import ws_storage.server
import ws_storage.impl.client

conf_mod = 'ws_storage.tests.conf.simple'

class Foo(object): pass

@pytest.fixture(scope='module')
def loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope='module')
def addr(loop):
    app, addr = ws_storage.server.start(loop, {
        'conf_mod': conf_mod,
        'conf_dir': os.path.join(os.environ['HOME'], 'config'),
        'd': True,
        'port': 0,
        })
    yield addr
    ws_storage.server.stop(loop, app)

class TestClient():

    def test(self, loop, addr):
        try:
            #self.setUp()
            loop.run_until_complete(self.go(loop, addr))
        finally:
            #self.tearDown()
            pass

    async def go(self, loop, addr):
        conf = modconf.import_class(
                conf_mod, 
                'Conf', 
                ('DEVELOP', os.path.join(os.environ['HOME'], 'config')))

        #client = ws_sheets_server.sockets.Client(port)
        
        #print(client.book_new())
        
        L = conf.LOGGING
        for l in L['loggers'].values():
            l['handlers'] = ['console']
        logging.config.dictConfig(L)
        
        logger = logging.getLogger(__name__)

        logger.debug('ws_stroage version = {}'.format(ws_storage.__version__))

        protocol = await ws_storage.impl.client.Storage.create(loop, addr[0], addr[1])

        print(protocol)
        
        if protocol.transport.is_closing():
            self.fail()

        lst = await protocol.list_files()

        assert lst is not None

        ###

        id_ = await protocol.next_id()
        print('id',id_)

        o = Foo()
        
        print('write')
        
        b = pickle.dumps(o)

        coro = protocol.write_binary(id_, b)
        print('coro',coro)
        res = await coro
        print(res)

        print('read')
        coro = protocol.read_binary(id_)
        print('coro', coro)
        b = await coro
 
        print('b', b)

        o = pickle.loads(b)

        print(o)
   
        assert isinstance(o, Foo)

    
    
    
    
