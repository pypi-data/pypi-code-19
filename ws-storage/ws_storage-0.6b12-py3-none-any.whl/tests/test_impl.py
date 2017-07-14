import os
import asyncio
import pickle
import logging
import logging.config

import pytest

import modconf
import ws_storage.impl.filesystem
import ws_storage.impl.as3
import ws_storage.impl.client

class Foo: pass

@pytest.mark.asyncio
@pytest.mark.parametrize('cls, storage_server', [
    (ws_storage.impl.filesystem.Storage, False),
    (ws_storage.impl.as3.Storage, False),
    (ws_storage.impl.client.Storage, True)],
    indirect=['storage_server'])
async def test(event_loop, cls, storage_server):

    args = {
            'dev': True,
            'conf_dir': os.path.join(os.environ['HOME'], 'config'),
            'console': True,
            }

    conf = modconf.import_class(
            'ws_storage.tests.conf.simple', 
            'Conf', 
            tuple(),
            args)
    
    logging.config.dictConfig(conf.LOGGING)

    if storage_server:
        _, addr = storage_server
        s = await cls.create(event_loop, addr[0], addr[1])
        assert not s.transport.is_closing()
    else:
        s = cls(conf, event_loop)

    await _test(s)

async def _test(s):
    f = Foo()

    b = pickle.dumps(f)
    
    id_ = await s.next_id()
    
    print('id =',id_)

    await s.write_binary(id_, b)

    b = await s.read_binary(id_)

    f = pickle.loads(b)

    print(f)
    
    await s.delete(id_)


