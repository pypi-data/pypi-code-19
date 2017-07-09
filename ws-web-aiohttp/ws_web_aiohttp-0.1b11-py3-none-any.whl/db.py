import sqlalchemy as sa

import ws_web_aiohttp.security.db as db

async def get_book(app, book_id):
    """
    :param book_id: id of book object
    """
    async with app['db_engine'].acquire() as conn:
        where = sa.and_(
                db.books.c.bookid == book_id)

        query = db.books.select().where(where)
        ret = await conn.execute(query)
        book = await ret.fetchone()
        return book

async def get_user(app, userid):
    """
    :param book_id: id of book object
    """
    async with app['db_engine'].acquire() as conn:
        where = sa.and_(
                db.users.c.userid == userid)

        query = db.users.select().where(where)
        ret = await conn.execute(query)
        user = await ret.fetchone()
        return user

async def get_user_by_user_id(app, user_id):
    """
    :param book_id: id of book object
    """
    async with app['db_engine'].acquire() as conn:
        where = sa.and_(
                db.users.c.id == user_id)

        query = db.users.select().where(where)
        ret = await conn.execute(query)
        user = await ret.fetchone()
        return user

async def get_users(app):
    """
    :param book_id: id of book object
    """
    async with app['db_engine'].acquire() as conn:
        #where = sa.and_(
        #        db.users.c.id == user_id)

        query = db.users.select()
        ret = await conn.execute(query)
        users = await ret.fetchall()
        #return user
        return users

async def get_user_books(app, user):
    """
    :param 
    """
    async with app['db_engine'].acquire() as conn:
        where = sa.and_(
                db.books.c.user_id == user.id)

        query = db.books.select().where(where)
        ret = await conn.execute(query)
        books = await ret.fetchall()
        return books

