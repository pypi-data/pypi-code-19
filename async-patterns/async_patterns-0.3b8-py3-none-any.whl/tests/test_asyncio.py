
async def a():
    raise Exception()

async def atest(loop):
    task = loop.create_task(a())

    await task

def test(loop):
    try:
        loop.run_until_complete(atest(loop))
    except: pass

