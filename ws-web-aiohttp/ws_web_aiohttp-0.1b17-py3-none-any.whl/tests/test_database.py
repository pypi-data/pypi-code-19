import asyncio
import unittest

import ws_sheets_server.packet
import ws_web_aiohttp.db
import ws_web_aiohttp.server

conf_mod = 'ws_web_aiohttp.tests.conf.simple'
conf_dir = None

def test(loop, addr_compute):
    loop.run_until_complete(atest(loop, conf_mod, conf_dir, addr_compute))

async def atest(loop, conf_mod, conf_dir, addr_compute):
    vargs = {
            'dev': True,
            'conf_dir': conf_dir,
            'addr_compute': addr_compute,
            #'console': True,
            }
    app = await ws_web_aiohttp.server.setup_app(
            conf_mod,
            conf_dir,
            vargs)

    app._set_loop(loop)
    
    await ws_web_aiohttp.server.on_startup(app)
    
    users = await ws_web_aiohttp.db.get_users(app)
    
    for user in users:

        print('user=',user)
    
        books = await ws_web_aiohttp.db.get_user_books(app, user)

        if not books:
            print('books is empty')
            if len(user[1]) >= 32:
                print('delete user')
                await ws_web_aiohttp.db.delete_user(app, user[0])
            continue
    
        proto = await ws_web_aiohttp.connections.open_book_proto(app)
        
        for book in books:
            print('  book=',book)

            if len(user[1]) >= 32:
                print('  delete book')
                ret = await ws_web_aiohttp.db.delete_book(app, book[0])
                print('  ret=', ret)
                continue
    
            proto.book_id = book[2]
        
            resp = await proto.request_sheet_data('0')
            print('  resp=',resp)
 
            if isinstance(resp, ws_sheets_server.packet.BookNotFound):
                print('  delete book')
                ret = await ws_web_aiohttp.db.delete_book(app, book[0])
                print('  ret=', ret)
        
        await proto.close()



