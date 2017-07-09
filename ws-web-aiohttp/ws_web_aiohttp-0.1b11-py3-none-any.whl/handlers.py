import functools
import json
import logging

import aiohttp
import aiohttp.web
import aiohttp_security
import aiohttp_session

import ws_sheets.tests.test_demos

import ws_sheets_server
import ws_sheets_server.packet

import ws_web_aiohttp
import ws_web_aiohttp.db
import ws_web_aiohttp.connections
import ws_web_aiohttp.security
import ws_web_aiohttp.security.wrappers
import ws_web_aiohttp.security.db as db

logger = logging.getLogger(__name__)

class User: pass

async def get_user(request):
    userid = await aiohttp_security.authorized_userid(request)

    session = await aiohttp_session.get_session(request)
    
    if userid:
        user = User()
        user.picture = session.get('picture','')
    else:
        user = None

    if userid:
        userdb = await ws_web_aiohttp.db.get_user(request.app, userid)
    else:
        userdb = None

    logger.info('userid={}'.format(userid))
    logger.info('userdb={}'.format(userdb))
    logger.info('user={}'.format(user))

    return userid, userdb, session, user

async def handler_index(request):
   
    userid, userdb, sessions, user = await get_user(request)

    #user = request.app['users'].get(userid, ws_web_aiohttp.security.User())

    template = request.app['template_env'].get_template('index.html')
    
    demos = ws_sheets.tests.test_demos.DEMOS.keys()
    
    text = template.render(
            user=user,
            demos=demos,
            prefix=str(request.app['PREFIX']),
            )
    
    response = aiohttp.web.Response(body=text)
    response.content_type = 'text/html'
    return response

@ws_web_aiohttp.security.wrappers.require_login()
async def handler_user_index(request):
    userid, userdb, sessions, user = await get_user(request)
    
    books = await ws_web_aiohttp.db.get_user_books(request.app, userdb)
    
    template = request.app['template_env'].get_template('user_index.html')
    
    text = template.render(
            prefix=str(request.app['PREFIX']),
            user=user,
            books=books)

    response = aiohttp.web.Response(body=text)
    response.content_type = 'text/html'
    return response

@ws_web_aiohttp.security.wrappers.require()
async def handler(request):
    userid, userdb, sessions, user = await get_user(request)
    
    logger.debug('host={}'.format(request.host))
    
    book_id = request.match_info.get('book_id')
    
    sheet_id = '0' # TODO save last viewed sheet in database

    template = request.app['template_env'].get_template('sheet.html')
    
    ws_url = '{}://{}{}'.format(request.app['SCHEME_WS'], request.app['conf'].HOST, str(request.app['PREFIX'] / 'ws'))
    
    logger.debug('ws_url = {}'.format(ws_url))

    text = template.render(
            prefix=str(request.app['PREFIX']),
            user=user,
            ws_url=ws_url,
            book_id=book_id,
            sheet_id=sheet_id,)
    
    response = aiohttp.web.Response(body=text)
    response.content_type = 'text/html'
    return response

async def book_new(request):
    userid = await aiohttp_security.authorized_userid(request)
    user = await ws_web_aiohttp.db.get_user(request.app, userid)
    
    logger.debug('book new. user = {}'.format(repr(user)))
    
    proto = await ws_web_aiohttp.connections.open_book_proto(request.app)
    res = await proto.request_new()
 
    logger.debug('insert user_id={} bookid={}'.format(user[0], proto.book_id))

    async with request.app['db_engine'].acquire() as conn:
        q = db.books.insert().values(user_id=user[0], bookid=proto.book_id)
        logger.debug('q={}'.format(q))
        result = await conn.execute(q)
        logger.debug('result {}'.format(result.rowcount))
        for row in result:
            logger.debug('row={}'.format(row))

    return proto

@ws_web_aiohttp.security.wrappers.require_login()
async def handler_book_new(request):
    name = request.match_info.get('name')

    proto = await book_new(request) # TODO add name parameter

    #return response
    
    id_ = proto.book_id
    # close proto?

    return aiohttp.web.HTTPFound(request.app['PREFIX'] / 'book/{}/'.format(id_))

@ws_web_aiohttp.security.wrappers.require_login()
async def handler_demo(request):

    name = request.match_info.get('name')

    logger.info('demo {}'.format(name))

    cls = ws_sheets.tests.test_demos.DEMOS[name]
    o = cls()

    proto = await book_new(request)

    o.setup(proto)

    return aiohttp.web.HTTPFound(request.app['PREFIX'] / 'book/{}/'.format(proto.book_id))

async def process_json_message(app, data, proto):

    logger.debug('json message')
    logger.debug('{}'.format(data))

    p = None

    async def f(p):
        await p.write_response_sheet_data(data['sheet_id'])

    if data['type'] == 'get_sheet_data':
        p = ws_sheets_server.packet.RequestSheetData(data['book_id'], data['sheet_id'])
    elif data['type'] == 'add_col':
        p = ws_sheets_server.packet.AddColumn(data['book_id'], data['sheet_id'], data['i'])
        p.callback_post.add_callback(functools.partial(p.write_response_sheet_data))
    elif data['type'] == 'add_row':
        p = ws_sheets_server.packet.AddRow(data['book_id'], data['sheet_id'], data['i'])
        p.callback_post.add_callback(functools.partial(p.write_response_sheet_data))
    elif data['type'] == 'set_script_pre':
        p = ws_sheets_server.packet.SetScriptPre(data['book_id'], data['text'])
        p.callback_post.add_callback(functools.partial(p.write_response_sheet_data, data['sheet_id']))
    elif data['type'] == 'set_script_post':
        p = ws_sheets_server.packet.SetScriptPost(data['book_id'], data['text'])
        p.callback_post.add_callback(functools.partial(p.write_response_sheet_data, data['sheet_id']))
    elif data['type'] == 'set_cell':
        p = ws_sheets_server.packet.SetCell(data['book_id'], data['sheet_id'], data['r'], data['c'], data['s'])
    else:
        logger.error('invalid type: {}'.format(data['type']))
    
    if p:
        logger.debug('write {}'.format(repr(p)))
        proto.write(p)

async def handler_websocket(request):
    logger.debug('websocket handler')
    logger.debug('url = {}'.format(request.url))
    ws = aiohttp.web.WebSocketResponse()
    
    await ws.prepare(request)

    proto = await ws_web_aiohttp.connections.open_book_proto_web(request.app, ws)

    logger.debug('ws: wait for message')
    async for msg in ws:
        logger.debug('ws: msg = {}'.format(repr(msg)))
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                try:
                    data = json.loads(msg.data)
                except Exception as e:
                    logger.warning(e)
                else:
                    await process_json_message(request.app, data, proto)

        elif msg.type == aiohttp.WSMsgType.ERROR:
            logger.error('ws connection closed with exception {}'.format(repr(ws.exception())))

    return ws

