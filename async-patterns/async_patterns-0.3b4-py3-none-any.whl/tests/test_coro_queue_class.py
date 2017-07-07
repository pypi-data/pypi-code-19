
import asyncio

from async_patterns.coro_queue import *

class Foo(CoroQueueClass):
    @CoroQueueClass.wrap
    async def a():
        await asyncio.sleep(1)

    @CoroQueueClass.wrap
    async def b(*args):
        await asyncio.sleep(1)

    @CoroQueueClass.wrap
    async def c(*args, **kwargs):
        await asyncio.sleep(1)

async def atest(loop):

    foo = Foo()
    foo._loop = loop

    foo.a()
    foo.b(0)
    foo.c(0, d=1)
    
    await foo.coro_queue.join()

    await foo.coro_queue.close()

def test(loop):
    loop.run_until_complete(atest(loop))


