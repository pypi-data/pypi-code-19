
import asyncio

import async_patterns.coro_queue

async def a():
    await asyncio.sleep(1)

async def b(*args):
    await asyncio.sleep(1)

async def c(*args, **kwargs):
    await asyncio.sleep(1)

async def d():
    await asyncio.sleep(1)
    raise Exception()

async def atest1(loop):
    q = async_patterns.coro_queue.CoroQueue(loop)

    q.schedule_run_forever()

    q.put_nowait(a)
    q.put_nowait(b, 0)
    q.put_nowait(c, 0, a=1)
    q.put_nowait(d)
    
    await q.join()

    await q.close()

async def atest2(loop):
    q = async_patterns.coro_queue.CoroQueue(loop)

    q.schedule_run_forever()

    q.put_nowait(a)
    q.put_nowait(a)
    q.put_nowait(a)
    
    await q.close()

def test1(loop):
    loop.run_until_complete(atest1(loop))

def test2(loop):
    loop.run_until_complete(atest2(loop))


