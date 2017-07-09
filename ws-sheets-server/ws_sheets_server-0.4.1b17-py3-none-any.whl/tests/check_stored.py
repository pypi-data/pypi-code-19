import asyncio
import pickle
import time
import os
import sys
import json
import logging
import logging.config
import subprocess
import traceback

import modconf
import ws_storage.impl.filesystem
import ws_sheets


conf_dir = os.path.join(os.environ['HOME'], 'config')
conf_mod = 'ws_sheets_server.tests.conf.simple'

def test(loop, addr_storage):
        
    loop.run_until_complete(go(loop, addr_storage))

async def go(loop, addr_storage):
    
    conf = modconf.import_class(conf_mod, 'Conf', ('DEVELOP',), folder=conf_dir)
    conf.log_console()
    logging.config.dictConfig(conf.LOGGING)

    stor = await ws_storage.impl.client.Storage.create(
            loop, addr_storage[0], addr_storage[1])
   
    print('storage={}'.format(stor))

    lst = await stor.list_files()
    
    print('files =',lst)

    fail = False
    for f in lst:
        if f == '_counter':
            print('skip', repr(f))
            continue
        try:
            print('f=',f)
            b = await stor.read_binary(f)

            o = pickle.loads(b)

            print(repr(o))
            #print(dir(o))
        except Exception as e:
            print(e)
            fail = True

    # TODO turn this back on
    #assert (not fail)


