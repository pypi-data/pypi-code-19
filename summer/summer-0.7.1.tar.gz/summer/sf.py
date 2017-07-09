# Copyright (C) 2009-2017 Martin Slouf <martinslouf@users.sourceforge.net>
#
# This file is a part of Summer.
#
# Summer is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""Module ``sf`` defines :py:class:`SessionFactory` class which is central
point for your ORM mapping and *SQL database* access providing connections
to database.

"""

import logging
import threading
import sqlalchemy
import sqlalchemy.engine
import sqlalchemy.orm
import sqlalchemy.orm.session

from .utils import Singleton
from .ex import SummerConfigurationException

logger = logging.getLogger(__name__)


class SessionProvider(object):
    """Class to be used as based for providing *SqlAlchemy* session.

    See default implementation in
    :py:class:`summer.sf.DefaultSessionProvider`.
    """

    def __init__(self):
        self._engine = None
        self._sessionmaker = None

    @property
    def engine(self) -> sqlalchemy.engine.Engine:
        """Get *SqlAlchemy* engine implementation.

        Returns:

            sqlalchemy.engine.Engine: *SqlAlchemy* engine implementation
        """
        return self._engine

    @property
    def sessionmaker(self) -> sqlalchemy.orm.sessionmaker:
        """Get *SqlAlchemy* session factory class.

        Returns:

            sqlalchemy.orm.sessionmaker: *SqlAlchemy* session factory class
        """
        return self._sessionmaker


class DefaultSessionProvider(SessionProvider):
    lock = threading.RLock()

    def __init__(self, uri: str, autocommit: bool = False, pool_recycle: int = 3600):
        """
        Args:

            uri (str): *SqlAlchemy*'s uri (ie. connection string)

            autocommit (bool): *SqlAlchemy*'s autocommit

            pool_recycle (int): *SqlAlchemy*'s pool recycling timeout
        """
        SessionProvider.__init__(self)
        self._uri = uri
        self._autocommit = autocommit
        self._pool_recycle = pool_recycle

    @property
    def uri(self):
        return self._uri

    @property
    def autocommit(self):
        return self._autocommit

    @property
    def pool_recycle(self) -> int:
        return self._pool_recycle

    @property
    def engine(self):
        if not self._engine:
            with DefaultSessionProvider.lock:
                if not self._engine:
                    try:
                        self._engine = sqlalchemy.engine.create_engine(self.uri, pool_recycle=self.pool_recycle)
                    except:
                        logger.exception("unable to create engine with pool recycle")
                        self._engine = sqlalchemy.engine.create_engine(self.uri)
        return self._engine

    @property
    def sessionmaker(self):
        if not self._sessionmaker:
            with DefaultSessionProvider.lock:
                if not self._sessionmaker:
                    self._sessionmaker = sqlalchemy.orm.session.sessionmaker(bind=self.engine,
                                                                             autocommit=self.autocommit)
        return self._sessionmaker


class SessionFactory(object, metaclass=Singleton):
    """Thread safe *SqlAlchemy* session provider."""

    class Local(threading.local):

        """Thread local session & connection wrapper."""

        def __init__(self, engine: sqlalchemy.engine.Engine, sessionmaker: sqlalchemy.orm.session.sessionmaker):
            threading.local.__init__(self)
            self._engine = engine
            self._sessionmaker = sessionmaker
            self._sqlalchemy_session = None
            self._connection = None
            self._active = False  # True if transaction is active

        def __del__(self):
            self.close()

        @property
        def sqlalchemy_session(self) -> sqlalchemy.orm.Session:
            """Get current *SqlAlchemy* session.

            Returns:

                sqlalchemy.orm.Session: existing of just created *SqlAlchemy* session.
            """
            if self._sqlalchemy_session:
                logger.debug("accessing session = %s", self._sqlalchemy_session)
            else:
                self._sqlalchemy_session = self._sessionmaker()
                logger.debug("new thread local session created, session = %s", self._sqlalchemy_session)
            return self._sqlalchemy_session

        @property
        def autocommit(self) -> bool:
            """Delegates to :py:meth:`sqlalchemy_session.autocommit`."""
            return self.sqlalchemy_session.autocommit

        @property
        def connection(self) -> sqlalchemy.engine.Connection:
            """Use :py:attr:`connection.connection` to obtain *Python* DB API
            connection.

            Returns:

                sqlalchemy.engine.Connection: current thread-bound *SqlAclhemy* connection

            """
            if not self._connection:
                self._connection = self._engine.connect()
            return self._connection

        @property
        def active(self) -> bool:
            """Get status of current *SqlAlchemy* transaction.

            Returns:

                bool: `True` if transaction is in progress, `False` otherwise.
            """
            return self._active

        def close(self):
            # NOTE martin 2016-09-17 -- direct access to attributes, not through properties
            if self._sqlalchemy_session:
                self._sqlalchemy_session.close()
                self._sqlalchemy_session = None
            if self._connection:
                self._connection.close()
                self._connection = None
            self._active = False

        def begin(self):
            assert not self.active
            if not self.sqlalchemy_session.is_active and not self.autocommit:
                self.sqlalchemy_session.begin()
            else:
                logger.debug("not starting transaction in autocommit mode or if another one is active")
            self._active = True

        def commit(self):
            assert self.active
            if not self.autocommit:
                self.sqlalchemy_session.commit()
            else:
                logger.debug("not committing in autocommit mode")
            self._active = False

        def rollback(self):
            assert self.active
            if not self.autocommit:
                self.sqlalchemy_session.rollback()
            else:
                logger.debug("not doing rollback in autocommit mode")
            self._active = False

    def __init__(self, session_provider: SessionProvider):
        """Creates :py:class:`SessionFactory` instance.

        Args:

            uri (str): *SqlAlchemy* connection string (including username
                       and password)

        """
        self._session_provider = session_provider
        self._engine = session_provider.engine
        self._sessionmaker = session_provider.sessionmaker
        self._metadata = sqlalchemy.MetaData(bind=self._engine)
        self._session = SessionFactory.Local(self._engine, self._sessionmaker)
        self._table_definitions = None
        self._class_mappings = None

    @property
    def metadata(self) -> sqlalchemy.MetaData:
        return self._metadata

    @property
    def table_definitions(self):
        """Get current table definitions.

        Returns:

            TableDefinitions: current :py:class:`TableDefinitions` instance
        """
        return self._table_definitions

    @table_definitions.setter
    def table_definitions(self, table_definitions):
        """Set table definitons.

        See :py:meth:`summer.context.Context.orm_init` method.

        """
        self._table_definitions = table_definitions
        self._table_definitions.define_tables(self)
        logger.info("table definitions registered: %s", self._metadata.tables)

    @property
    def class_mappings(self):
        """Get current class mappings.

        Returns:

            ClassMappings: current :py:class:`ClassMappings` instance
        """
        return self._class_mappings

    @class_mappings.setter
    def class_mappings(self, class_mappings):
        """Set class mappings.

        See :py:meth:`summer.context.Context.orm_init` method.

        """
        if self.table_definitions is None:
            msg = "unable to register mappings -- set table definitions first"
            raise SummerConfigurationException(msg)
        self._class_mappings = class_mappings
        self._class_mappings.create_mappings(self)
        logger.info("class mappings registered")

    @property
    def session(self):
        """Get current thread-local *SqlAlchemy session* wrapper (creating one, if
        non-exististent).

        Returns:

            SessionFactory.Local: existing or just created *SqlAlchemy session* wrapper
        """
        return self._session

    @property
    def sqlalchemy_session(self) -> sqlalchemy.orm.Session:
        """Delegates to :py:meth:`SessionFactory.Local.sqlalchemy_session`."""
        return self.session.sqlalchemy_session

    @property
    def connection(self) -> sqlalchemy.engine.Connection:
        """Delegates to :py:meth:`SessionFactory.Local.connection`."""
        return self.session.connection

    @property
    def dialect(self) -> sqlalchemy.engine.Dialect:
        """Get *SqlAlchemy* dialect.

        Returns:

            sqlalchemy.engine.Dialect: current *SqlAlchemy* dialect
        """
        return self._engine.dialect

    @property
    def sqlite_dialect(self) -> bool:
        """*SQLite* is great database for testing or local access, but not designed
        for multi-threaded/-process applications.  Sometimes it is handy to
        know you are using it to bypass its limitations.

        Returns:

            bool: `True` if running over sqlite, `False` otherwise.

        """
        import sqlalchemy.dialects.sqlite
        return isinstance(self.dialect, sqlalchemy.dialects.sqlite.dialect)

    def create_schema(self):
        """Create database schema using *SqlAlchemy*.  Call once
        :py:attr:`table_definitions` are set.

        Use with caution -- will destroy all your data!
        """
        if self.table_definitions is None:
            msg = "unable to create schema -- set table definitions first"
            raise SummerConfigurationException(msg)
        # delegate call to ORM layer
        self.metadata.drop_all()
        self.metadata.create_all()


class AbstractTableDefinitions(object):
    """
    Container for *SqlAlchemy* table definitions.  Registers itself at
    session factory.  A callback class -- use to provide table definitions
    to ORM.

    See :py:meth:`summer.context.Context.orm_init` method.
    """

    def define_tables(self, session_factory: SessionFactory):
        """Override in subclasses to define database tables."""
        pass


class AbstractClassMappings(object):
    """Container for *SqlAlchemy* mappings.  Registers itself at session
    factory.  A callback class -- use to provide class mappings to ORM.

    See :py:meth:`summer.context.Context.orm_init` method.
    """

    def create_mappings(self, session_factory: SessionFactory):
        """Override in subclasses to define mappings (tables to ORM classes --
        entities).
        """
        pass
