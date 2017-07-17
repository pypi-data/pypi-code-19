import asyncio

import pytest

from async_patterns.context import AsyncContextManager

@AsyncContextManager
async def acontext():
    print('enter')
    yield
    print('exit')

@pytest.mark.asyncio
async def test():

    async with acontext() as a:
        await asyncio.sleep(0)


