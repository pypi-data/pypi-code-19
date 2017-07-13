from . import Rowset

def _iter_rowset (cur):
    while True:
        rows = cur.fetchmany()
        if not rows:
            break
        yield from map(tuple, rows)

def _iter_rowsets (cur):
    if cur.description is None:
        return
    while True:
        columns = [d[0] for d in cur.description]
        rows = _iter_rowset(cur)
        yield sqlgap.Rowset(columns, rows)
        if cur.nextset() is None:
            break

class ConnFactorySqlGap:
    def __init__ (self, conn_factory):
        self._conn_factory = conn_factory

    @classmethod
    def from_module (cls, module, *args, **kwargs):
        return cls(lambda: module.connect(*args, **kwargs))

    def execute (self, query, query_args=()):
        with self._conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(query, query_args)
                yield from self._iter_rowsets(cur)
