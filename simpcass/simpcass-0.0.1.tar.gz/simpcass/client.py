import math
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement, SimpleStatement
from cassandra import InvalidRequest


class CassandraClient:
    def __init__(self, server, port, keyspace=None):
        self._cluster = Cluster([server], port=port)
        self._keyspace = keyspace

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cluster.shutdown()

    def _try_get_session(self):
        for i in range(0,10):
            try:
                return self._cluster.connect(self._keyspace) if self._keyspace else self._cluster.connect()
            except Exception as e:
                if i >= 9:
                    raise
                else:
                    print('WARN: Error encountered connecting to Cassandra on attempt {}: {}'.format(i, e))
                    continue

    def execute(self, cql, args=None):
        session = self._try_get_session()
        if args is None:
            rows = session.execute(cql)
        else:
            rows = session.execute(cql, args)
        session.shutdown()
        return rows

    def _execute_batch(self, session, statements, args, sub_batches):
        sub_batch_size = math.ceil(len(statements) / sub_batches)
        for sub_batch in range(0, sub_batches):
            batch = BatchStatement()
            start_index = min(sub_batch * sub_batch_size, len(statements))
            end_index = min((sub_batch + 1) * sub_batch_size, len(statements))
            for i in range(start_index, end_index):
                batch.add(SimpleStatement(statements[i]), args[i])
            session.execute(batch)

    def execute_batch(self, statements, args):
        session = self._try_get_session()
        try:
            for sub_batches in range(1, len(statements) + 1):
                try:
                    self._execute_batch(session, statements, args, sub_batches)
                    return
                except InvalidRequest:
                    if len(statements) == sub_batches:
                        raise
                    print(
                        """
                        An error occured on a batch of length {}, split into {} sub_batches.
                        Trying again, with more sub_batches.
                        """.format(len(statements), sub_batches)
                    )
        finally:
            session.shutdown()


