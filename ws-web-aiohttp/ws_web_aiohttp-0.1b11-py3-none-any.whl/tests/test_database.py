import asyncio
import unittest

import ws_web_aiohttp.db
import ws_web_aiohttp.server

def test(loop):
    loop.run_until_complete(atest())

async def atest():

    app = await ws_web_aiohttp.server.setup_app(
            'ws_web_aiohttp.tests.conf.simple_console_secure',
            None,
            True,
            {})
 
    await ws_web_aiohttp.server.on_startup(app)

    users = await ws_web_aiohttp.db.get_users(app)

    print('users=',users)

    user = await ws_web_aiohttp.db.get_user_by_user_id(app, 1)

    print('user=',user)

    books = await ws_web_aiohttp.db.get_user_books(app, user)

    print('books=',books)

