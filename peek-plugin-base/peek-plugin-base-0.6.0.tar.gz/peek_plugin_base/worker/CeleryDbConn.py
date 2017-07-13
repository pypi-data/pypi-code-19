import logging
from threading import Lock
from typing import Iterable, Optional

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.schema import Sequence

logger = logging.getLogger(__name__)

_dbConnectString = None
__dbEngine = None
__ScopedSession = None


# For celery, an engine is created per worker
def getDbEngine():
    global __dbEngine

    if _dbConnectString is None:
        msg = "CeleryDbConn initialisation error"
        logger.error(msg)
        raise Exception(msg)

    if not __dbEngine:
        __dbEngine = create_engine(
            _dbConnectString,
            echo=False,
            pool_size=4,  # This is per fork
            max_overflow=10,  # Number that the pool size can exceed when required
            pool_timeout=20,  # Timeout for getting conn from pool
            pool_recycle=1200  # Reconnect?? after 10 minutes
        )

    return __dbEngine


def getDbSession():
    global __ScopedSession

    if not __ScopedSession:
        __ScopedSession = scoped_session(sessionmaker(bind=getDbEngine()))

    return __ScopedSession()


_sequenceMutex = Lock()


def prefetchDeclarativeIds(Declarative, count) -> Optional[Iterable[int]]:
    """ Prefetch Declarative IDs

    :return: An iterable iterating over the new IDs to use
    """

    if not count:
        logger.debug("Count was zero, no range returned")
        return

    conn = getDbEngine().connect()
    transaction = conn.begin()
    try:
        _sequenceMutex.acquire()

        sequence = Sequence('%s_id_seq' % Declarative.__tablename__,
                            schema=Declarative.metadata.schema)
        sql ='SELECT NEXT VALUE FOR "%s"."%s"' % (sequence.schema, sequence.name)
        startId = conn.execute(sql).fetchone()[0] + 1
        nextStartId = startId + count

        conn.execute('alter sequence "%s"."%s" restart with %s'
                     % (sequence.schema, sequence.name, nextStartId))

        transaction.commit()

        _sequenceMutex.release()

        return iter(range(startId, nextStartId))

    finally:
        conn.close()
