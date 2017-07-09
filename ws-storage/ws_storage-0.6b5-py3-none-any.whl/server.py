
import asyncio
import functools
import logging
import logging.config

logger = logging.getLogger(__name__)

import modconf
import async_patterns
import async_patterns.protocol
import async_patterns.coro_queue
import ws_storage.impl.as3
import ws_storage.impl.filesystem

class ServerClientProtocol(async_patterns.protocol.Protocol):
    def __init__(self, loop, app):
        logger.debug('{} created'.format(self.__class__.__name__))
        super(ServerClientProtocol, self).__init__(loop)
        logger.debug('super initialized')
        self.app = app

class Application(async_patterns.coro_queue.CoroQueueClass):
    def __init__(self, loop, conf):
        self.loop = loop
        self.conf = conf

        super(Application, self).__init__(loop=loop)

        factory = {
                'FILESYSTEM': ws_storage.impl.filesystem.Storage,
                'AS3': ws_storage.impl.as3.Storage,
                }

        logger.debug('impl={}'.format(repr(self.conf.IMPL)))

        self.storage = factory[self.conf.IMPL](self.conf, self.loop)
        
    @async_patterns.CoroQueueClass.wrap
    async def write_binary(self, id_, b):
        return (await self.storage.write_binary(id_, b))

    @async_patterns.CoroQueueClass.wrap
    async def read_binary(self, id_):
        res = await self.storage.read_binary(id_)

        if isinstance(res, Exception):
            raise res
    
        logger.debug('read binary id = {} len = {} bytes'.format(repr(id_), len(res)))

        return res

    @async_patterns.CoroQueueClass.wrap
    async def list_files(self):
        return (await self.storage.list_files())

    async def close(self):
        await super(Application, self).close()
        
        self.server.close()
        await self.server.wait_closed()


def start(loop, args):
    conf = modconf.import_class(
            args['conf_mod'], 
            'Conf', 
            ('DEVELOP' if args['d'] else 'DEPLOY', args['conf_dir'], args.get('impl','AS3')),
            kwargs={
                'port': args['port'],
                },
            folder=args['conf_dir'])

    logging.config.dictConfig(conf.LOGGING)

    app = Application(loop, conf)

    coro = loop.create_server(
            functools.partial(ServerClientProtocol, loop, app),
            'localhost', 
            conf.PORT)
    
    logger.debug('start server')
    app.server = loop.run_until_complete(coro)

    addr = app.server.sockets[0].getsockname()
    port = addr[1]
    
    logger.debug('serving on {}'.format(addr))
    logger.debug('port = {}'.format(port))
    logger.debug('ws_storage version = {}'.format(ws_storage.__version__))
    
    return app, addr

def stop(loop, app):
    logger.debug('closing')
    # Close the server
    loop.run_until_complete(app.close())

def runserver(args):
    loop = asyncio.get_event_loop()

    app, port = start(loop, args)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.debug('got keyboard interrupt')
    except Exception as e:
        logger.error(e)

    stop(loop, app)






