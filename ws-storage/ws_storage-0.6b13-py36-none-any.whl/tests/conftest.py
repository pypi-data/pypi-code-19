import os

import pytest

import ws_storage.server

@pytest.fixture(scope='module')
async def storage_server(request, event_loop):
    print('fixture storage_server param={}'.format(request.param))
    if request.param:

        args = {
                'conf_mod': 'ws_storage.tests.conf.simple',
                'conf_dir': os.path.join(os.environ['HOME'], 'config'),
                'dev': True,
                'port': 0,
                }
    
        async with ws_storage.server.Application(event_loop, args) as (app, addr):
            yield app, addr
    else:
        yield None

