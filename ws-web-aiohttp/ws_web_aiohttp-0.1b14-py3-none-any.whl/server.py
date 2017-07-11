#!/usr/bin/env python3
import functools
import logging
import os
import jinja2

import aiohttp
import aiohttp.web
import aiohttp_security
import aiohttp_session.redis_storage
import aioredis
import aiopg
import aiopg.sa
import sys
import json
import requests_oauthlib
import ssl
import modconf
import argparse
import asyncio
import pickle
import base64
import yarl
#import cryptography


import ws_sheets_server
import ws_sheets_server.packet

import ws_web_aiohttp.handlers
import ws_web_aiohttp.security.handlers
import ws_web_aiohttp.security.db_auth
import ws_web_aiohttp.security.db

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(__file__)

SCHEME = 'http'
SCHEME_WS = 'ws'

async def setup_db(db_engine):

    logger.info('setup_db')

    async with db_engine.acquire() as conn:
        with open(os.path.join(BASE_DIR, 'sql', 'init.sql')) as f:
            ret = (await conn.execute(f.read()))
        #ret = ws_web_aiohttp.security.db.metadata.create_all(bind=conn)
    
async def on_startup(app):
    
    db_engine = await aiopg.sa.create_engine(
            user=app['conf'].PG.user,
            password=app['conf'].PG.password,
            database=app['conf'].PG.db,
            host=app['conf'].PG.host)
   
    #aiohttp_session.setup(app, 
    #        aiohttp_session.redis_storage.RedisStorage(redis_pool))

    await setup_db(db_engine)

    aiohttp_security.setup(app,
            aiohttp_security.SessionIdentityPolicy(),
            ws_web_aiohttp.security.db_auth.DBAuthorizationPolicy(db_engine))

    app['db_engine'] = db_engine

    # compute server address
    app['address_server_compute'] = await get_addr_server_compute(app)

    print("app['conf'].ADDR_COMPUTE", app['conf'].ADDR_COMPUTE)
    print('address_server_compute  ', app['address_server_compute'])

async def on_shutdown(app):
    app['redis_pool'].close()

#async def setup_sessions(app):
#    fernet_key = cryptography.fernet.Fernet.generate_key()
#    secret_key = base64.urlsafe_b64decode(fernet_key)
#    aiohttp_session.setup(app, EncryptedCookieStorage(secret_key))

async def get_addr_server_compute(app):
    a = app['args'].get('addr_compute', None)
    if a is None:
        return app['conf'].ADDR_COMPUTE
    
    if a == 'local':
        # start our own compute server
        args = {
                'conf_mod': 'ws_sheets_server.tests.conf.simple',
                'd': True,
                'port': 0,
                }
        addr, _ = await ws_sheets_server.server_aio.start(app.loop, args)
        return addr
    
    return a

async def setup_app(conf_mod, conf_dir, vargs):
    """
    :param conf_mod: config module name
    :param conf_dir: config module search path
    :param vargs: dict of command line options
    """
    print(vargs)
    
    #redis_pool = await aioredis.create_pool(('localhost', 6379))
    kwargs = {
            'dev': vargs.get('dev', False),
            'port': vargs.get('port', None),
            'console': vargs.get('console', False),
            'addr_compute': vargs.get('addr_compute', None),
            'test_key': vargs.get('test_key', None),
            'conf_dir': conf_dir,
            }

    conf = modconf.import_class(conf_mod, 'Conf', tuple(),
            kwargs=kwargs,
            folder=conf_dir)

    logging.config.dictConfig(conf.LOGGING)

    redis_pool = await aioredis.create_pool(('localhost', 6379))

    #await setup_sessions(app)

    app = aiohttp.web.Application(middlewares=[
        aiohttp_session.session_middleware(aiohttp_session.redis_storage.RedisStorage(redis_pool))])

    app['args'] = vargs
    app['conf'] = conf
    app['test_key'] = conf.test_key
    app['redis_pool'] = redis_pool

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    app['oauth'] = {}
    app['users'] = {}

    app['conf'] = conf

    logging.config.dictConfig(app['conf'].LOGGING)

    app['template_env'] = jinja2.Environment(
            loader=jinja2.PackageLoader('ws_web_aiohttp', 'templates'))

    app['SCHEME'] = app['conf'].SCHEME
    app['SCHEME_WS'] = app['conf'].SCHEME_WS
    app['PREFIX'] = yarl.URL(vargs['prefix']) if vargs.get('prefix', None) is not None else yarl.URL(app['conf'].PREFIX)

    # routes
    app.router.add_get(str(app['PREFIX']) + '', ws_web_aiohttp.handlers.handler_index)
    app.router.add_get(str(app['PREFIX']) + 'user/', ws_web_aiohttp.handlers.handler_user_index)
    app.router.add_get(str(app['PREFIX']) + 'book/{book_id}/', ws_web_aiohttp.handlers.handler)
    app.router.add_get(str(app['PREFIX']) + 'book_new/{name}/', ws_web_aiohttp.handlers.handler_book_new)
    app.router.add_get(str(app['PREFIX']) + 'demo/{name}/', ws_web_aiohttp.handlers.handler_demo)
    app.router.add_get(str(app['PREFIX']) + 'ws', ws_web_aiohttp.handlers.handler_websocket)
    
    app.router.add_get(str(app['PREFIX']) + 'google_oauth2_login', ws_web_aiohttp.security.handlers.handler_google_oauth2_login)
    app.router.add_get(str(app['PREFIX']) + 'google_oauth2_response', ws_web_aiohttp.security.handlers.handler_google_oauth2_response)
    app.router.add_get(str(app['PREFIX']) + 'logout', ws_web_aiohttp.security.handlers.logout)

    app['LOGIN_URL'] = 'google_oauth2_login'

    # static routes
    if app['conf'].DEV:
        app.router.add_static(str(app['PREFIX']) + 'static/other/handsontable',
                path=os.path.join(os.environ['HOME'], 'web_sheets/handsontable/dist'),
                name='static_hot')
     
        app.router.add_static(str(app['PREFIX']) + 'static/other/google',
                path=os.path.join(os.environ['HOME'], 'static/google'),
                name='static_google')
   
        app.router.add_static(str(app['PREFIX']) + 'static/',
                path=os.path.join(BASE_DIR, 'static'),
                name='static')

    else:
        app.router.add_static(str(app['PREFIX']) + 'static/other',
                path=app['conf'].STATIC_DIR,
                name='static_other')

        app.router.add_static(str(app['PREFIX']) + 'static/',
                path=os.path.join(BASE_DIR, 'static'),
                name='static')

    logger.debug('starting web app')
    logger.debug('prefix = {}'.format(app['PREFIX']))

    return app

def runserver(vargs):
    loop = asyncio.get_event_loop()
    coro = setup_app(vargs.get('conf_mod'), vargs.get('conf_dir'), vargs)
    app = loop.run_until_complete(coro)
    
    logger.debug('ssl  = {}'.format(app['conf'].SSL_CONTEXT))
    logger.debug('port = {}'.format(app['conf'].PORT))

    aiohttp.web.run_app(
            app, 
            port=app['conf'].PORT, 
            ssl_context=app['conf'].SSL_CONTEXT)



