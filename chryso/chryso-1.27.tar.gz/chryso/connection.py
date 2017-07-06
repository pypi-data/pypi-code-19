import contextlib
import logging
import threading
import weakref

import sqlalchemy
import sqlalchemy.pool

import chryso.errors

LOGGER = logging.getLogger(__name__)

class Transaction():
    def __init__(self, engine, parent):
        self.engine = engine
        self.parent = parent
        self.resolved = False

    @property
    def depth(self):
        depth = 0
        parent = self.parent
        while parent:
            depth += 1
            parent = parent.parent
        return depth

    def savepoint(self):
        command = "SAVEPOINT chryso_{}".format(self.depth) if self.parent else "BEGIN"
        self.execute(command)
        LOGGER.debug("Executed '%s'", command)

    def rollback(self):
        if self.resolved:
            raise chryso.errors.TransactionError("This transaction is already resolved, you cannot roll it back now")
        command = "ROLLBACK TO SAVEPOINT chryso_{}".format(self.depth) if self.parent else "ROLLBACK"
        self.execute(command)
        LOGGER.debug("Executed '%s'", command)
        self.resolved = True

    def commit(self):
        if self.resolved:
            raise chryso.errors.TransactionError("This transaction is already resolved, you cannot commit it now")
        command = "RELEASE SAVEPOINT chryso_{}".format(self.depth) if self.parent else "COMMIT"
        self.execute(command)
        LOGGER.debug("Executed '%s'", command)
        self.resolved = True

    def execute(self, *args, **kwargs):
        try:
            result = self.engine.execute(*args, **kwargs)
            return result
        except (sqlalchemy.exc.DBAPIError, sqlalchemy.exc.StatementError) as e:
            raise chryso.errors.parse_exception(e)

class PoolForThreads(sqlalchemy.pool.Pool):
    def __init__(self, creator, **kwargs):
        kwargs['use_threadlocal'] = True
        self.creator = creator
        super().__init__(creator, **kwargs)
        self._local = threading.local()
        self._all_connections = set()
        self.kwargs = kwargs

    def recreate(self):
        LOGGER.info("Recreating PoolForThreads")
        return self.__class__(
            creator     = self.creator,
            **self.kwargs)

    def dispose(self):
        for connection in self._all_connections:
            try:
                connection.close()
            except Exception: # pylint: disable=broad-except
                pass
        self._all_connections.clear()

    def status(self):
        return "PoolForThreads id:{}".format(id(self))

    def _do_return_conn(self, conn):
        pass

    def _do_get(self):
        try:
            c = self._local.current()
            if c:
                return c
        except AttributeError:
            pass
        LOGGER.info("Creating connection to DB for %s (%s)", threading.current_thread().name, threading.current_thread().ident)
        c = self._create_connection()
        self._local.current = weakref.ref(c)
        self._all_connections.add(c)
        return c

class Engine():
    def __init__(self, uri, tables, track_queries=False, echo=False, set_timezone=True):
        self._engine       = sqlalchemy.create_engine(
            uri,
            echo=echo,
            isolation_level = 'AUTOCOMMIT',
            pool_recycle    = 3600,
            poolclass       = PoolForThreads,
        )
        self.queries        = []
        self.tables         = tables
        self.track_queries  = track_queries
        self._local         = threading.local()

        if track_queries:
            # pylint: disable=unused-variable
            @sqlalchemy.event.listens_for(self._engine, 'before_execute')
            def receive_execute(conn, clauseelement, multiparams, params): # pylint: disable=unused-argument
                self.queries.append(clauseelement)

        if set_timezone:
            # pylint: disable=unused-variable
            @sqlalchemy.event.listens_for(sqlalchemy.pool.Pool, 'connect')
            def set_utc(dbapi, record): # pylint: disable=unused-argument
                cursor = dbapi.cursor()
                cursor.execute('SET TIME ZONE UTC')
                cursor.close()

    def create_all(self):
        LOGGER.debug("Creating all tables")
        self.tables.metadata.create_all(self._engine)
        LOGGER.debug("DB tables created")

    def drop_all(self):
        LOGGER.debug("Dropping all database tables")
        self.tables.metadata.drop_all(self._engine)
        LOGGER.debug("All database tables dropped")

    def execute(self, query, *args, **kwargs):
        try:
            return self._engine.execute(query, *args, **kwargs)
        except (sqlalchemy.exc.DBAPIError, sqlalchemy.exc.StatementError) as e:
            raise chryso.errors.parse_exception(e)

    @contextlib.contextmanager
    def atomic(self):
        """
        Transaction context manager.

        Will commit the transaction on successful completion of the block or roll it back on error

        Supports nested usage (via savepoints)
        """
        if not hasattr(self._local, 'transactions'):
            self._local.transactions   = []
        parent = self._local.transactions[-1] if self._local.transactions else None
        transaction = Transaction(self, parent)
        self._local.transactions.append(transaction)
        transaction.savepoint()

        try:
            yield transaction
        except:
            transaction.rollback()
            raise
        else:
            if not transaction.resolved:
                transaction.commit()
        finally:
            self._local.transactions.pop()

    def reset(self):
        self.drop_all()
        self.create_all()
        self.reset_queries()

    def reset_queries(self):
        self.queries = []

def store(engine):
    store.engine = engine
store.engine = None

def get():
    return store.engine
