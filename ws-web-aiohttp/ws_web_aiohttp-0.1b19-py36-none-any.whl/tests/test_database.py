import asyncio

import pytest

import ws_sheets_server.packet
import ws_web_aiohttp.db
import ws_web_aiohttp.server

conf_mod = 'ws_web_aiohttp.tests.conf.simple'
conf_dir = None

@pytest.mark.asyncio
async def test(event_loop, web, addr_compute):
    await _test(event_loop, conf_mod, conf_dir, web, addr_compute)

async def _test(event_loop, conf_mod, conf_dir, web, addr_compute):

    web_app, web_uris = web

    users = await ws_web_aiohttp.db.get_users(web_app)
    
    for user in users:

        print('user=',user)
    
        books = await ws_web_aiohttp.db.get_user_books(web_app, user)

        if not books:
            print('books is empty')
            if len(user[1]) >= 32:
                print('delete user')
                await ws_web_aiohttp.db.delete_user(web_app, user[0])
            continue
    
        proto = await ws_web_aiohttp.connections.open_book_proto(web_app)
        
        for book in books:
            print('  book=',book)

            if len(user[1]) >= 32:
                print('  delete book')
                ret = await ws_web_aiohttp.db.delete_book(web_app, book[0])
                print('  ret=', ret)
                continue
    
            proto.book_id = book[2]
        
            resp = await proto.request_sheet_data('0')
            print('  resp=',resp)
 
            if isinstance(resp, ws_sheets_server.packet.BookNotFound):
                print('  delete book')
                ret = await ws_web_aiohttp.db.delete_book(web_app, book[0])
                print('  ret=', ret)
        
        await proto.close()



