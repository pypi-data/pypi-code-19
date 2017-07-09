import asyncio
import functools
import json
import logging
import numpy

import ws_sheets_server
import ws_sheets_server.client_aio

import ws_web_aiohttp

logger = logging.getLogger(__name__)

def cells_array(cells):
    
    def f(c):
        v = c.value
        v = repr(v)
        #if isinstance(v, str): v = "\"" + v + "\""
        try:
            return json.dumps([c.string, v])
        except Exception as e:
            logger.error('error while json stringifying {}\n{}'.format(repr(v), e))
            raise

    return numpy.vectorize(f, otypes=[str])(cells).tolist()

class BookProtocol(ws_sheets_server.client_aio.BookProtocol):
    def __init__(self, loop, ws):
        super(BookProtocol, self).__init__(loop)
        self.ws = ws

    async def async_packet_received(self, packet):
        await super(BookProtocol, self).async_packet_received(packet)
        
        logger.debug('{} received {}'.format(self.__class__.__name__, packet.__class__.__name__))
        
        if isinstance(packet, ws_sheets_server.packet.ResponseSheetData):
            self.ws.send_json({
                'type':'response_sheet_data',
                'cells':cells_array(packet.cells),
                'script_pre':packet.script_pre,
                'script_pre_output':packet.script_pre_output,
                'script_post':packet.script_post,
                'script_post_output':packet.script_post_output,
                })

async def open_book_proto_web(app, ws):
    addr = app['address_server_compute']
    host = addr[0]
    port = addr[1]
    logger.debug('addr = {}'.format(repr(addr)))
    logger.debug('host = {}'.format(repr(host)))
    logger.debug('port = {}'.format(repr(port)))

    coro = app.loop.create_connection(
            functools.partial(BookProtocol, app.loop, ws),
            host,
            port,
            )
    
    transport, proto = await coro

    logger.debug('transport={}'.format(repr(transport)))

    return proto

async def open_book_proto(app):
    addr = app['address_server_compute']
    host = addr[0]
    port = addr[1]
    logger.debug('addr = {}'.format(repr(addr)))
    logger.debug('host = {}'.format(repr(host)))
    logger.debug('port = {}'.format(repr(port)))

    coro = app.loop.create_connection(
            functools.partial(ws_sheets_server.client_aio.BookProtocol, app.loop),
            host,
            port,
            )
    
    transport, proto = await coro

    logger.debug('transport={}'.format(repr(transport)))

    return proto

