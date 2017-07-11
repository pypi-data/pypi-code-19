import asyncio
import logging
import sqlalchemy as sa

from aiohttp_security.abc import AbstractAuthorizationPolicy
#from passlib.hash import sha256_crypt

from . import db

logger = logging.getLogger(__name__)

class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, dbengine):
        self.dbengine = dbengine

    async def authorized_userid(self, identity):
        async with self.dbengine.acquire() as conn:
            where = sa.and_(
                    db.users.c.userid == identity,
                        sa.not_(db.users.c.disabled))

            query = db.users.count().where(where)
            
            ret = await conn.scalar(query)
            
            if ret:
                return identity
            else:
                return None

    async def permits(self, identity, bookid, context=None):
        logger.debug('permits identity={} bookid={}'.format(identity, bookid))

        if identity is None:
            return False

        async with self.dbengine.acquire() as conn:
            where = sa.and_(
                    db.users.c.userid == identity,
                    sa.not_(db.users.c.disabled))

            query = db.users.select().where(where)
            ret = await conn.execute(query)
            user = await ret.fetchone()
            
            logger.debug('user={}'.format(user))

            if user is not None:
                user_id = user[0]

                where = db.books.c.bookid == bookid
                query = db.books.select().where(where)
                ret = await conn.execute(query)
                result = await ret.fetchone()

                logger.debug('book={}'.format(result))

                if result is not None:
                    if result.user_id == user.id:
                        return True

            return False

async def check_credentials(db_engine, userid):
    async with db_engine.acquire() as conn:
        where = sa.and_(
                db.users.c.userid == userid,
                sa.not_(db.users.c.disabled))

        query = db.users.select().where(where)

        ret = await conn.execute(query)
        
        user = await ret.fetchone()
        
        if user is None:
            await conn.execute(db.users.insert().values(userid=userid))

    return True





