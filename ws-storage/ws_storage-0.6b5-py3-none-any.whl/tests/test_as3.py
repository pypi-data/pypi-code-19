import os
import asyncio
import pickle
import logging
import logging.config

import modconf
import ws_storage.impl.as3

class Foo: pass

class TestAs3:
    def test(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.go())

    async def go(self):
        conf = modconf.import_class(
                'ws_storage.tests.conf.simple', 
                'Conf', 
                ('DEVELOP', os.path.join(os.environ['HOME'], 'config')))
        
        conf.log_console()

        logging.config.dictConfig(conf.LOGGING)

        s = ws_storage.impl.as3.Storage(conf, self.loop)
        
        f = Foo()

        b = pickle.dumps(f)
        
        id_ = await s.next_id()
        
        print('id =',id_)

        await s.write_binary(id_, b)

        b = await s.read_binary(id_)

        f = pickle.loads(b)

        print(f)

