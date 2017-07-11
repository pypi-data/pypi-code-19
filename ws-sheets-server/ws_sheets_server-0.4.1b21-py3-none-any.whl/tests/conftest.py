import asyncio
import os
import sys
import time

import pytest

import ws_storage.server
import ws_sheets_server.server_aio

@pytest.fixture
def loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    print('closing event loop')
    
    pending = asyncio.Task.all_tasks()
    for t in pending:
        if not t.done():
            print(t)
    
    for t in pending:
        if not t.done():
            #raise Exception()
            pass

    loop.close()

@pytest.fixture
def addr_storage(loop):
    args = {
        'conf_mod': 'ws_storage.tests.conf.simple',
        'conf_dir': os.path.join(os.environ['HOME'], 'config'),
        'd': True,
        'port': 0,
        }

    app, addr = ws_storage.server.start(loop, args)
    
    time.sleep(3)

    yield addr
    
    ws_storage.server.stop(loop, app)

    print('exiting storage server fixture')

@pytest.fixture
def addr_compute(loop, addr_storage):
    vargs = {
        'conf_mod': 'ws_sheets_server.tests.conf.simple',
        'port': 0,
        'addr_storage': addr_storage,
        'd': True,
        'console': True,
        }
    
    app = ws_sheets_server.server_aio.Application(loop, vargs)
    
    addr, app = loop.run_until_complete(app.__aenter__())
    
    print('yield port')
    yield addr
    print('after yield port')
    
    print('stop compute server')
    print(app.books)
    print(app.protos)

    loop.run_until_complete(app.__aexit__(None, None, None))


