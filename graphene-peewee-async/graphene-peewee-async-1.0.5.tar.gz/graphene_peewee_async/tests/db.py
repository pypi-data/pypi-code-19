import asyncio
import peewee

# from peewee import SqliteDatabase
from peewee_async import AsyncDatabase


# class Proxy(object):
#     __slots__ = ["_obj", "__weakref__"]
#
#     def __init__(self, obj):
#         object.__setattr__(self, "_obj", obj)
#
#     #
#     # proxying (special cases)
#     #
#     def __getattribute__(self, name):
#         if name == 'release':
#             return super().__getattribute__(name)
#         return getattr(object.__getattribute__(self, "_obj"), name)
#
#     def __delattr__(self, name):
#         delattr(object.__getattribute__(self, "_obj"), name)
#
#     def __setattr__(self, name, value):
#         if name == 'release':
#             return super().__setattr__(name, value)
#         setattr(object.__getattribute__(self, "_obj"), name, value)
#
#     def __nonzero__(self):
#         return bool(object.__getattribute__(self, "_obj"))
#
#     def __str__(self):
#         return str(object.__getattribute__(self, "_obj"))
#
#     def __repr__(self):
#         return repr(object.__getattribute__(self, "_obj"))
#
#     #
#     # factories
#     #
#     _special_names = [
#         '__abs__', '__add__', '__and__', '__call__', '__cmp__', '__coerce__',
#         '__contains__', '__delitem__', '__delslice__', '__div__', '__divmod__',
#         '__eq__', '__float__', '__floordiv__', '__ge__', '__getitem__',
#         '__getslice__', '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__',
#         '__idiv__', '__idivmod__', '__ifloordiv__', '__ilshift__', '__imod__',
#         '__imul__', '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__',
#         '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__',
#         '__long__', '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__',
#         '__neg__', '__oct__', '__or__', '__pos__', '__pow__', '__radd__',
#         '__rand__', '__rdiv__', '__rdivmod__', '__reduce__', '__reduce_ex__',
#         '__repr__', '__reversed__', '__rfloorfiv__', '__rlshift__', '__rmod__',
#         '__rmul__', '__ror__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__',
#         '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__sub__',
#         '__truediv__', '__xor__', 'next',
#     ]
#
#     @classmethod
#     def _create_class_proxy(cls, theclass):
#         """creates a proxy for the given class"""
#
#         def make_method(name):
#             def method(self, *args, **kw):
#                 return getattr(object.__getattribute__(self, "_obj"), name)(*args, **kw)
#
#             return method
#
#         namespace = {}
#         for name in cls._special_names:
#             if hasattr(theclass, name):
#                 namespace[name] = make_method(name)
#         return type("%s(%s)" % (cls.__name__, theclass.__name__), (cls,), namespace)
#
#     def __new__(cls, obj, *args, **kwargs):
#         """
#         creates an proxy instance referencing `obj`. (obj, *args, **kwargs) are
#         passed to this class' __init__, so deriving classes can define an
#         __init__ method of their own.
#         note: _class_proxy_cache is unique per deriving class (each deriving
#         class must hold its own cache)
#         """
#         try:
#             cache = cls.__dict__["_class_proxy_cache"]
#         except KeyError:
#             cls._class_proxy_cache = cache = {}
#         try:
#             theclass = cache[obj.__class__]
#         except KeyError:
#             cache[obj.__class__] = theclass = cls._create_class_proxy(obj.__class__)
#         ins = object.__new__(theclass)
#         theclass.__init__(ins, obj, *args, **kwargs)
#         return ins


class AsyncCursor:

    def __init__(self, cursor):
        self.cursor = cursor

    @asyncio.coroutine
    def execute(self, *args, **kwargs):
        self.cursor.execute(*args, **kwargs)

    @asyncio.coroutine
    def fetchone(self, *args, **kwargs):
        self.cursor.fetchone(*args, **kwargs)

    @asyncio.coroutine
    def fetchall(self, *args, **kwargs):
        self.cursor.fetchone(*args, **kwargs)


class AsyncSqliteConnection:
    """Asynchronous database connection pool.
    """
    def __init__(self, *, database=None, loop=None, timeout=None, **kwargs):
        # self.pool = None
        self.db = None
        self.loop = loop
        self.database = database
        # self.timeout = timeout or aiopg.DEFAULT_TIMEOUT
        self.connect_kwargs = kwargs

    @asyncio.coroutine
    def acquire(self):
        """Acquire connection from pool.
        """
        # return (yield from self.pool.acquire())
        pass

    def release(self, conn):
        """Release connection to pool.
        """
        # self.pool.release(conn)
        pass

    @asyncio.coroutine
    def connect(self):
        """Create connection pool asynchronously.
        """
        # self.pool = yield from aiopg.create_pool(
        #     loop=self.loop,
        #     timeout=self.timeout,
        #     database=self.database,
        #     **self.connect_kwargs)
        self.db = peewee.SqliteDatabase(self.database, **self.connect_kwargs)
        self.db.connect()

    @asyncio.coroutine
    def close(self):
        """Terminate all pool connections.
        """
        self.db.close()
        # self.pool.terminate()
        # yield from self.pool.wait_closed()

    @asyncio.coroutine
    def cursor(self, conn=None, *args, **kwargs):
        """Get a cursor for the specified transaction connection
        or acquire from the pool.
        """
        in_transaction = conn is not None
        if not conn:
            # conn = yield from self.acquire()
            conn = self.db
        cursor = conn.get_cursor(*args, **kwargs)
        from sqlite3 import Cursor
        # NOTE: `cursor.release` is an awaitable object!
        o = self.release_cursor(cursor, in_transaction=in_transaction)
        cursor = AsyncCursor(cursor)
        # setattr(cursor, 'release', o)
        cursor.release = o
        return cursor

    @asyncio.coroutine
    def release_cursor(self, cursor, in_transaction=False):
        """Release cursor coroutine. Unless in transaction,
        the connection is also released back to the pool.
        """
        conn = cursor.connection
        cursor.close()
        if not in_transaction:
            self.release(conn)


class AsyncSqliteMixin(AsyncDatabase):
    """Mixin for `peewee.PostgresqlDatabase` providing extra methods
    for managing async connection.
    """

    def init_async(self, conn_cls=AsyncSqliteConnection,
                   enable_json=False, enable_hstore=False):
        self._async_conn_cls = conn_cls
        # self._enable_json = enable_json
        # self._enable_hstore = enable_hstore

    @property
    def connect_kwargs_async(self):
        """Connection parameters for `aiopg.Connection`
        """
        kwargs = self.connect_kwargs.copy()
        kwargs.update({
            # 'minsize': self.min_connections,
            # 'maxsize': self.max_connections,
            # 'enable_json': self._enable_json,
            # 'enable_hstore': self._enable_hstore,
        })
        return kwargs

    @asyncio.coroutine
    def last_insert_id_async(self, cursor, model):
        """Get ID of last inserted row.

        NOTE: it's a copy-paste, not sure how to make it better
        https://github.com/05bit/peewee/blob/2.3.2/peewee.py#L2907
        """
        meta = model._meta
        schema = ''
        if meta.schema:
            schema = '%s.' % meta.schema

        if meta.primary_key.sequence:
            seq = meta.primary_key.sequence
        elif meta.auto_increment:
            seq = '%s_%s_seq' % (meta.db_table, meta.primary_key.db_column)
        else:
            seq = None

        if seq:
            cursor.execute("SELECT CURRVAL('%s\"%s\"')" % (schema, seq))
            result = (cursor.fetchone())[0]
            return result


class SqliteDatabase(AsyncSqliteMixin, peewee.SqliteDatabase):
    """PosgreSQL database driver providing **single drop-in sync** connection
    and **single async connection** interface.

    Example::

        database = PostgresqlDatabase('test')

    See also:
    http://peewee.readthedocs.io/en/latest/peewee/api.html#PostgresqlDatabase
    """
    def init(self, database, **kwargs):
        # self.min_connections = 1
        # self.max_connections = 1
        super().init(database, **kwargs)
        self.init_async()

    @property
    def use_speedups(self):
        return False

    @use_speedups.setter
    def use_speedups(self, value):
        pass
