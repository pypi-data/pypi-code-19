# -*- coding: utf-8 -*-

import inspect

from . import utils

__all__ = ['wrap']


class ProxyCursor(object):

    __INTERFACES = ['before_insert', 'before_update', 'after_insert', 'after_update']

    def __init__(self, cursor, handlers=None):
        self.__cursor = cursor
        self.__handlers = self.__validate_handlers(handlers)
        self.__cursor.execute = self.execute

    def __getattr__(self, attr):
        return getattr(self.__cursor, attr)

    def __validate_handlers(self, handlers):
        if not handlers:
            return None

        for handler in handlers:
            before_insert = utils.get_bound_method(handler, 'before_insert')
            before_update = utils.get_bound_method(handler, 'before_after')
            after_insert = utils.get_bound_method(handler, 'after_insert')
            after_update = utils.get_bound_method(handler, 'after_update')

            if not (before_insert or after_insert or before_update or after_update):
                msg = 'Not implement the handler interface: {0}'
                raise TypeError(msg.format(handler))

        return handlers

    def execute(self, query, args=None):
        backframe = filter(lambda cur: '__execute_with_handlers' in cur[3], inspect.stack())
        if len(backframe) > 0:
            return self.__execute(query, args)

        if self.__handlers:
            result = self.__execute_with_handlers(query, args)
        else:
            result = self.__execute(query, args)
        return result

    def __execute_with_handlers(self, query, args=None):
        mogrified_query = self.__cursor.mogrify(query, args)
        dml_type, tables = utils.parser.extract_tables(mogrified_query)

        if dml_type == 'SELECT':
            return self.__execute(query, args)

        if len(tables) == 0:
            # switch ownership to the original cursor when no table
            # found after parsing a SQL statement.
            return self.__execute(query, args)

        def pre_execute(obj, names, dml_type):
            names = filter(lambda name: name.startswith('before'), names)
            for name in names:
                if name.endswith(dml_type):
                    getattr(obj, name)(cursor=self.__cursor)

        def post_execute(obj, names, dml_type, result):
            names = filter(lambda name: name.startswith('after'), names)
            for name in names:
                if name.endswith(dml_type):
                    getattr(obj, name)(result=result, cursor=self.__cursor)

        def interfaces(obj):
            attrs = [m for m in dir(obj) if callable(getattr(obj, m))]
            return filter(lambda attr: attr in ProxyCursor.__INTERFACES, attrs)

        result = None
        handlers = filter(lambda h: h.tblname in tables, self.__handlers)

        if len(handlers) == 0:
            # switch ownership to the original cursor when no handler found
            # for the given table in a SQL statement to execute.
            return self.__execute(query, args)

        for handler in handlers:
            funcs = interfaces(handler)
            pre_execute(handler, funcs, dml_type.lower())
            result = self.__execute(query, args)
            lastrowid = self.__cursor.lastrowid
            post_execute(handler, funcs, dml_type.lower(), result)
            self.__cursor.lastrowid = lastrowid
        return result

    def __execute(self, query, args=None):
        while self.__cursor.nextset():
            pass

        query = self.__cursor.mogrify(query, args)
        result = self.__cursor._query(query)
        self.__cursor._executed = query
        return result


wrap = ProxyCursor
