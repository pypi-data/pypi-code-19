import logging
from threading import Lock
from typing import Iterable, Optional

from peek_plugin_base.storage.AlembicEnvBase import isPostGreSQLDialect, isMssqlDialect
from peek_plugin_base.storage.DbConnection import _commonPrefetchDeclarativeIds
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

    This function prefetches a chunk of IDs from a database sequence.
    Doing this allows us to preallocate the IDs before an insert, which significantly
    speeds up :

    * Orm inserts, especially those using inheritance
    * When we need the ID to assign it to a related object that we're also inserting.

    :param Declarative: The SQLAlchemy declarative class.
        (The class that inherits from DeclarativeBase)

    :param count: The number of IDs to prefetch

    :return: An iterable that dispenses the new IDs
    """
    return _commonPrefetchDeclarativeIds(
        getDbEngine(), _sequenceMutex, Declarative, count
    )
