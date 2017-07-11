import asyncio
import unittest

import ws_web_aiohttp.db
import ws_web_aiohttp.server

conf_mod = 'ws_web_aiohttp.tests.conf.simple'
conf_dir = None

def test(loop):
    _test(loop, conf_mod, conf_dir)

def _test(loop, conf_mod, conf_dir):
    loop.run_until_complete(atest(conf_mod, conf_dir))

async def atest(conf_mod, conf_dir):
    vargs = {
            'dev': True,
            'conf_dir': conf_dir,
            }
    app = await ws_web_aiohttp.server.setup_app(
            conf_mod,
            conf_dir,
            vargs)
    
    await ws_web_aiohttp.server.on_startup(app)
    
    users = await ws_web_aiohttp.db.get_users(app)
    
    print('users=',users)
    
    user = await ws_web_aiohttp.db.get_user_by_user_id(app, 1)
    
    print('user=',user)
    
    books = await ws_web_aiohttp.db.get_user_books(app, user)
    
    print('books=',books)

