
import asyncio

import async_patterns.coro_queue

async def a():
    await asyncio.sleep(1)

async def b(*args):
    await asyncio.sleep(1)

async def c(*args, **kwargs):
    await asyncio.sleep(1)

async def atest(loop):
    q = async_patterns.coro_queue.CoroQueue(loop)

    q.schedule_run_forever()

    q.put_nowait(a)
    q.put_nowait(b, 0)
    q.put_nowait(c, 0, d=1)
    
    await q.join()

    await q.close()

def test(loop):
    loop.run_until_complete(atest(loop))


