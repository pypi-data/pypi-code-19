import logging
from sqlalchemy.engine import base
from sqlalchemy.engine.strategies import DefaultEngineStrategy
from sqlalchemy.exc import OperationalError, DatabaseError

from oe_daemonutils.circuit import DaemonCircuitBreaker

logger = logging.getLogger(__name__)


class RetryEngine(base.Engine):
    def __init__(self, *args, **kwargs):
        super(RetryEngine, self).__init__(*args, **kwargs)

    def create(self, entity, **kwargs):  # pragma no cover
        super(RetryEngine, self).create(entity, **kwargs)

    def drop(self, entity, **kwargs):  # pragma no cover
        super(RetryEngine, self).drop(entity, **kwargs)

    def connect(self, **kwargs):
        """
        Return a new :class:`.Connection` object.

        The :class:`.Connection` object is a facade that uses a DBAPI
        connection internally in order to communicate with the database.  This
        connection is procured from the connection-holding :class:`.Pool`
        referenced by this :class:`.Engine`. When the
        :meth:`~.Connection.close` method of the :class:`.Connection` object
        is called, the underlying DBAPI connection is then returned to the
        connection pool, where it may be used again in a subsequent call to
        :meth:`~.Engine.connect`.

        This method will keep trying to get a connection forever
        """

        connection_circuit = DaemonCircuitBreaker(self._connection_cls, logger,
                                                  (IOError, OperationalError, DatabaseError))
        return connection_circuit.call(self, **kwargs)

    def contextual_connect(self, close_with_result=False, **kwargs):
        """Return a :class:`.Connection` object which may be part of some
        ongoing context.

        By default, this method does the same thing as :meth:`.Engine.connect`.
        Subclasses of :class:`.Engine` may override this method
        to provide contextual behavior.

        :param close_with_result: When True, the first :class:`.ResultProxy`
          created by the :class:`.Connection` will call the
          :meth:`.Connection.close` method of that connection as soon as any
          pending result rows are exhausted. This is used to supply the
          "connectionless execution" behavior provided by the
          :meth:`.Engine.execute` method.

        This method will keep trying to get a connection forever
        """

        connection_circuit = DaemonCircuitBreaker(self._connection_cls, logger,
                                                  (IOError, OperationalError, DatabaseError))
        return connection_circuit.call(
            self,
            self._wrap_pool_connect(self.pool.connect, None),
            close_with_result=close_with_result,
            **kwargs)

    def _wrap_pool_connect(self, fn, connection):
        connection_circuit = DaemonCircuitBreaker(super(RetryEngine, self)._wrap_pool_connect, logger,
                                                  (IOError, OperationalError, DatabaseError))
        return connection_circuit.call(fn, connection)


class RetryEngineStrategy(DefaultEngineStrategy):
    """Strategy for configuring an Engine that keeps trying to get a connection."""

    name = 'retry'
    engine_cls = RetryEngine


RetryEngineStrategy()
