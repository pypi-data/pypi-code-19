import asyncio
import functools
import aiohttp.web
import aiohttp_security
import logging
import yarl

logger = logging.getLogger(__name__)

def require():
    def wrapper(f):
        @functools.wraps(f)
        async def wrapped(request): #async def wrapped(self, request):
            logger.debug('require wrapper')
            logger.debug('url={}'.format(request.url))

            book_id = request.match_info.get('book_id')

            userid = await aiohttp_security.authorized_userid(request)

            logger.debug('userid  = {}'.format(userid))
            logger.debug('book_id = {}'.format(book_id))
            
            has_perm = await aiohttp_security.permits(request, book_id)
            if not has_perm:
                message = 'user has no permission {}'.format(book_id)
                logger.info(message)
                
                q = {}
                q.update(request.query)
                q['next'] = request.rel_url.path
                url = yarl.URL(request.app['PREFIX'] / str(request.app['LOGIN_URL'])).with_query(q)
                return aiohttp.web.HTTPFound(url)

            #return (await f(self, request))
            return (await f(request))
        return wrapped
    return wrapper

def require_login():
    def wrapper(f):
        @functools.wraps(f)
        async def wrapped(request): #async def wrapped(self, request):
            logger.debug('require_login wrapper')
            logger.debug('url={}'.format(request.url))
            
            userid = await aiohttp_security.authorized_userid(request)

            logger.debug('userid = {}'.format(userid))
            
            if not userid:
                logger.info('not signed in')

                q = {}
                q.update(request.query)
                q['next'] = request.rel_url.path
                url = yarl.URL(request.app['PREFIX'] / str(request.app['LOGIN_URL'])).with_query(q)

                logger.debug('forwarding to {}'.format(url))

                return aiohttp.web.HTTPFound(url)

            #return (await f(self, request))
            return (await f(request))
        return wrapped
    return wrapper


