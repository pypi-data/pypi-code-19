
import asyncio

from async_patterns.coro_queue import *

class Foo(CoroQueueClass):
    @CoroQueueClass.wrap
    async def a(self):
        await asyncio.sleep(1)

    @CoroQueueClass.wrap
    async def b(self, b1):
        await asyncio.sleep(1)

    @CoroQueueClass.wrap
    async def c(self, c1, c2=0):
        await asyncio.sleep(1)

async def atest(loop):

    foo = Foo()
    foo._loop = loop

    await foo.a()
    await foo.b(0)
    await foo.c(0, c2=1)
    
    await foo.coro_queue.join()

    await foo.coro_queue.close()

def test(loop):
    loop.run_until_complete(atest(loop))


