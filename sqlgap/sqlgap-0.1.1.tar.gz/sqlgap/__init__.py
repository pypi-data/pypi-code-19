class Rowset:
    def __init__ (self, names, rows):
        self.names = names
        self.rows = rows

class SqlGap:
    def execute (self, query, query_args=()):
        return []

class PassthroughSqlGap:
    def __init__ (self, parent):
        self._parent = parent

    def execute (self, query, query_args=()):
        return self._parent.execute(query, query_args)
