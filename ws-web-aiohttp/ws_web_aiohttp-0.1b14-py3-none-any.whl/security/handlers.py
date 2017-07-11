import os
import binascii
import aiohttp
import aiohttp_security
import aiohttp_session
import functools
import json
import logging
import yarl

import requests_oauthlib

import ws_sheets_server
import ws_sheets_server.packet

import ws_web_aiohttp
import ws_web_aiohttp.connections

logger = logging.getLogger(__name__)

async def handler_google_oauth2_login(request):
    logger.debug('login handler {}'.format(request.url))
    logger.debug('next = {}'.format(request.GET['next']))
    
    next_url = request.GET['next']

    app = request.app
    conf = app['conf']

    #redirect_uri = app['SCHEME'] + '://' + conf.google_oauth2.URL + '/google_oauth2_response' + '?next=' + request.GET['next']
    redirect_uri = app['SCHEME'] + '://' + conf.google_oauth2.URL + str(app['PREFIX'] / 'google_oauth2_response')

    logger.debug('redirect_uri = {}'.format(redirect_uri))

    # detect testing environment
    test_key = request.query.get('test_key', None)
    if test_key:
        logger.info('get test_key={}'.format(test_key))
        if test_key == app['test_key']:
            logger.info('its an older code but it checks out')
            state = binascii.hexlify(os.urandom(32)).decode()
            request.app['oauth'][state] = (None, next_url)
            url = yarl.URL(redirect_uri).with_query({'state':state,'test_key':test_key})
            return aiohttp.web.HTTPFound(url)
        else:
            logger.error('bad test_key')
    else:
        logger.info('no test_key')

    scope = ['https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile']
    
    oauth = requests_oauthlib.OAuth2Session(
            conf.google_oauth2.client_id,
            redirect_uri=redirect_uri,
            scope=scope)

    authorization_url, state = oauth.authorization_url(
            'https://accounts.google.com/o/oauth2/auth',
            # access_type and approval_prompt are Google specific extra
            # parameters.
            access_type="offline", approval_prompt="force")

    logger.debug('state = {}'.format(state))
    
    # Store the oauth object using state as identifier.
    # It will be needed in the response handler
    request.app['oauth'][state] = (oauth, next_url)
    
    return aiohttp.web.HTTPFound(authorization_url)

async def get_userid(request, oauth, session):
    app = request.app
    conf = app['conf']
    
    logger.debug('request scheme = {}'.format(request.scheme))
    logger.debug('request host   = {}'.format(request.host))
    logger.debug('request url    = {}'.format(request.url))

    #authorization_response = request.scheme + '://' + request.host + request.path_qs
    #authorization_response = 'https://' + conf.HOST + str(app['PREFIX']) + request.path_qs
    authorization_response = str(request.url)

    logger.debug('authorization_response = {}'.format(authorization_response))

    token = oauth.fetch_token(
            'https://accounts.google.com/o/oauth2/token',
            authorization_response=authorization_response,
            # Google specific extra parameter used for client
            # authentication
            client_secret=conf.google_oauth2.client_secret)

    r = oauth.get('https://www.googleapis.com/oauth2/v1/userinfo').json()

    session['oauth_token'] = token
    session['picture'] =  r['picture']

    userid = r['id']
    
    return userid

async def handler_google_oauth2_response(request):
    app = request.app
    conf = app['conf']
    
    session = await aiohttp_session.get_session(request)
    logger.info('session={}'.format(session))
    
    #state = request.match_info.get('state')
    
    state = request.GET['state']
    (oauth, next_url) = request.app['oauth'][state]
 
    test_key = request.query.get('test_key', None)
    if test_key:
        if test_key == app['test_key']:
            userid = test_key
        else:
            return aiohttp.web.HTTPForbidden()
    else:
        userid = await get_userid(request, oauth, session)

    logger.debug('google response')
    logger.debug('state = {}'.format(state))
    logger.debug('next  = {}'.format(next_url))
    
    response = aiohttp.web.HTTPFound(next_url)
    
    db_engine = request.app['db_engine']
    
    if (await ws_web_aiohttp.security.db_auth.check_credentials(db_engine, userid)):
        await aiohttp_security.remember(request, response, userid)
        return response

    return web.HTTPUnauthorized(
            body=b'Auth failed')

async def logout(request):
    response = aiohttp.web.HTTPFound('/')
    await aiohttp_security.forget(request, response)
    return response




