import asyncio
import functools

import async_patterns.protocol

class To:
    async def __call__(self, proto):
        print(self.__class__)
        f = From()
        f.response_to = self.message_id
        proto.write(f)

class ToError:
    async def __call__(self, proto):
        print(self.__class__)
        raise Exception(self.__class__)

class ToSlow:
    async def __call__(self, proto):
        print(self.__class__)
        await asyncio.sleep(100)

class From:
    async def __call__(self, _):
        print(self.__class__)

sp = None

class ServerProtocol(async_patterns.protocol.Protocol):
    def __init__(self, loop):
        global sp
        print(self.__class__)
        super(ServerProtocol, self).__init__(loop)
        sp = self

class ClientProtocol(async_patterns.protocol.Protocol):
    def __init__(self, loop):
        print(self.__class__)
        super(ClientProtocol, self).__init__(loop)

async def atest(loop):
    server = await loop.create_server(functools.partial(ServerProtocol, loop), port=0)
    addr = server.sockets[0].getsockname()
    host = addr[0]
    port = addr[1]
    
    print()
    print('serving on', addr)
    print('wait for server start')
    await asyncio.sleep(1)
    
    _, client = await loop.create_connection(functools.partial(ClientProtocol, loop), host, port)
    
    resp = await client.write(To())

    print('resp =', resp)

    client.write(ToError())
    client.write(ToSlow())
    
    await asyncio.sleep(1)
    
    print(sp.queue_packet_acall)

    await sp.close()

    server.close()
    await server.wait_closed()

def test(loop):
    loop.run_until_complete(atest(loop))

