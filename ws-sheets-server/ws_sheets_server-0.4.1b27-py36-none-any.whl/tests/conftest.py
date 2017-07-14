import asyncio
import functools
import os
import sys
import time

import pytest

import ws_storage.server
import ws_sheets_server.server_aio

@pytest.fixture
async def addr_storage(event_loop):
    args = {
        'conf_mod': 'ws_storage.tests.conf.simple',
        'conf_dir': os.path.join(os.environ['HOME'], 'config'),
        'dev': True,
        'port': 0,
        }
    
    async with ws_storage.server.Application(event_loop, args) as (app, addr):
        await asyncio.sleep(3)
        yield addr
    
    print('exiting storage server fixture')

@pytest.fixture
async def addr_compute(event_loop, addr_storage):
    args = {
        'conf_mod': 'ws_sheets_server.tests.conf.simple',
        'port': 0,
        'addr_storage': addr_storage,
        'dev': True,
        #'console': True,
        }
    
    async with ws_sheets_server.server_aio.Application(event_loop, args) as (app, addr):
        yield app, addr
    
@pytest.fixture
async def compute_client(event_loop, addr_compute):

    _, addr = addr_compute

    _, c = await event_loop.create_connection(
            functools.partial(ws_sheets_server.client_aio.BookProtocol, event_loop),
            addr[0],
            addr[1],
            )
    
    yield c
    

