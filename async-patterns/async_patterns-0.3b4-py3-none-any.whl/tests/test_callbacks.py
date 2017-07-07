import asyncio

from async_patterns import Callbacks

def test():
    cb = Callbacks()
    
    l = []

    def func1():
        l.append(1)
    
    def func2():
        l.append(2)
    
    cb.add_callback(func1)
    cb.add_callback(func2)
    
    cb()

    assert l == [1, 2]

def test_async(loop):
    cb = Callbacks()
    
    l = []

    async def func1():
        l.append(1)
    
    async def func2():
        l.append(2)
    
    cb.add_callback(func1)
    cb.add_callback(func2)
    
    loop.run_until_complete(cb.acall())

    assert l == [1, 2]

