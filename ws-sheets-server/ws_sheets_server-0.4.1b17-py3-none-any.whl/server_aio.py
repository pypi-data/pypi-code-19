import argparse
import asyncio
import concurrent.futures
import json
import numpy
import functools
import logging
import logging.config
import modconf
import pickle
import sys

import ws_storage
import async_patterns.coro_queue
import async_patterns.protocol
import ws_storage.impl.client

import ws_sheets
import ws_sheets_server.packet

logger = logging.getLogger(__name__)

class ServerClientProtocol(async_patterns.protocol.Protocol):
    def __init__(self, loop, app):
        super(ServerClientProtocol, self).__init__(loop)
        self.app = app
        self.app.protos.append(self)

class ScriptStringDescriptor(object):
    def __get__(self, obj, objtype):
        return obj.get_string()

    def __set__(self, obj, value):
        return obj.set_string(value)

class ScriptOutputDescriptor(object):
    def __get__(self, obj, objtype):
        return obj.get_output()

    def __set__(self, obj, value):
        raise RuntimeError('read only')

class Script(object):
    string = ScriptStringDescriptor()
    output = ScriptOutputDescriptor()

    def __init__(self, book, script):
        self.book = book
        self.__script = script

    def get_string(self):
        return self.book._put(self.__get_string)

    async def __get_string(self):
        return self.__script.get_string()

    def set_string(self, value):
        return self.book._put(self.__set_string, value)

    async def __set_string(self, s):
        self.__script.set_string(s)

    def get_output(self):
        return self.book._put(self.__get_output)

    async def __get_output(self):
        return self.__script.output

class Sheet(object):
    def __init__(self, book, sheet):
        self.book = book
        self.__sheet = sheet

    async def getitem(self, args):
        return (await self.book._put(functools.partial(self.__getitem, args)))

    async def __getitem(self, future, args):
        return self.__sheet.__getitem__(args)

    async def setitem(self, args, string):
        return self.book._put(functools.partial(self.__setitem, args, string))

    async def __setitem(self, args, string):
        return self.__sheet.__setitem__(args, string)

    async def add_row(self, i):
        return self.book._put(self.__add_row, i)

    async def __add_row(self, i):
        self.__sheet.add_row(i)

    async def add_column(self, i):
        return self.book._put(self.__add_column, i)

    async def __add_column(self, i):
        self.__sheet.add_column(i)

    async def convert_cells(self):
        return (await self.book._put(functools.partial(self.__convert_cells)))

    async def __convert_cells(self):
        def f(c):
            if c is None:
                return ws_sheets_server.Cell('','')
            
            if False:
                v = c.value
                if isinstance(v, str):
                    v = "\"" + v + "\""
                else:
                    v = str(v)
            else:
                v = c.value
            
            return ws_sheets_server.Cell(c.string, v)

        fv = numpy.vectorize(f, otypes=[ws_sheets_server.Cell])

        return fv(self.__sheet.cells.cells)

class Book(async_patterns.coro_queue.CoroQueueClass):
    def __init__(self, app, loop, id_, book):
        self.app = app
        self.loop = loop
        self.id_ = id_
        self.__book = book

        self.__coro_queue = async_patterns.coro_queue.CoroQueue(loop)
        
        #super(Book, self).__init__(self.__coro_queue)
        async_patterns.coro_queue.CoroQueueClass.__init__(self, self.__coro_queue, loop)

        self.sheets = dict((i, Sheet(self, s)) for i, s in self.__book.sheets.items())

        self.script_pre = Script(self, self.__book.script_pre)
        self.script_post = Script(self, self.__book.script_post)

    def schedule_run_forever(self):
        self.__coro_queue.schedule_run_forever()

    def _put(self, f, *args):
        return self.__coro_queue.put_nowait(f, *args)

    @async_patterns.coro_queue.CoroQueueClass.wrap
    async def calculate(self):
        task = self.loop.run_in_executor(None, functools.partial(self.__book.do_all))
        return (await task)

    async def write(self):
        return self._put(self.__write)

    async def __write(self):
        #self.app.storage.save_object(self.id_)
        #await self.app.write_book(self.id_)
        b = pickle.dumps(self.__book)
        await self.app.storage.write_binary(self.id_, b)

    async def set_docs(self, s):
        return (await self._put(self.__set_docs, s))
    
    async def __set_docs(self, s):
        self.__book.set_docs(s)

    @property
    def docs(self):
        return self.__book.docs

    async def close(self):
        logger.debug('book close')
        await self.__coro_queue.close()

class Application(object):
    def __init__(self, conf, loop, concurrent=False):
        self.loop = loop
        self.conf = conf
        self.concurrent = concurrent
        self.books = {}

        self.protos = []

    async def get_storage(self):
        addr = self.conf.STORAGE_ADDR
        host, port = addr[0], addr[1]

        self.storage = await ws_storage.impl.client.Storage.create(
                    self.loop,
                    host,
                    port)
        # TODO make sure the effect this deprecated line is performed elsewhere
        #self.storage.set_object_new_args((self.conf.conf_sheets.Settings,))

    async def read_book(self, id_):
        b = await self.storage.read_binary(id_)
        
        book = pickle.loads(b)
        
        bookc = Book(
                self,
                self.loop,
                id_,
                book)

        bookc.schedule_run_forever()

        self.books[id_] = bookc
        return bookc

    async def get_book(self, book_id):
        if book_id in self.books:
            return self.books[book_id]

        book = await self.read_book(book_id)
        return book

    async def book_new(self):
        id_ = await self.storage.next_id()

        bookc = Book(
                self,
                self.loop,
                id_,
                ws_sheets.Book(self.conf.conf_sheets.Settings))

        bookc.schedule_run_forever()

        self.books[id_] = bookc
       
        return id_, bookc


    async def close(self):
        logger.debug('close')
        # Close the server
        self.server.close()
        await self.server.wait_closed()

        logger.debug('open books')
        for book_id, book in self.books.items():
            logger.debug('  {}'.format(book_id))
            await book.close()

        logger.debug('protocols')
        for p in self.protos:
            logger.debug('  {}'.format(repr(p)))
            await p.close()

        await asyncio.sleep(5)

async def start(loop, args):
    kwargs = {
            'port': args.get('port', None),
            'console': args.get('console', False),
            }

    conf = modconf.import_class(args['conf_mod'], 'Conf', ('DEVELOP' if args.get('d', False) else 'DEPLOY',),
            kwargs=kwargs,
            folder=args.get('conf_dir',None))

    logging.config.dictConfig(conf.LOGGING)

    loop.set_debug(True)
    
    executor = concurrent.futures.ProcessPoolExecutor()

    app = Application(conf, loop)
    app.executor = executor
    
    await app.get_storage()

    app.server = await loop.create_server(
            functools.partial(ServerClientProtocol, loop, app),
            'localhost', 
            conf.PORT)
    
    addr = app.server.sockets[0].getsockname()
    
    logger.debug('Serving on {}'.format(addr))
    
    return addr, app

async def stop(loop, app):
    logger.debug('stop')
    await app.close()
    
def runserver(args):
    logger = logging.getLogger(__name__)
    loop = asyncio.get_event_loop()

    port, app = loop.run_until_complete(start(loop, args))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.exception('exception occured\n{}'.format(e))
    finally:
        loop.run_until_complete(stop(loop, app))

    loop.close()





