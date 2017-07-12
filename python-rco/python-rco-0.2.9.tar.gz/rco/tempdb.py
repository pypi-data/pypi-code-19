# -*- coding: utf-8 -*-

import rco
import functools
import cherrypy
import logging
import importlib
from cherrybase.utils import PoolsCatalog
from cherrybase import rpc
import re


catalog = PoolsCatalog ('TEMPDB')


def use_tempdb (autocommit = True, position = 1):
    def _wrap (method):
        @functools.wraps (method)
        def _wrapped (*args, **kwargs):
            pool_name = args [position]
            connection = catalog.get (pool_name)
            _largs = list (args)
            _largs.insert (position + 1, connection)
            try:
                result = method (*_largs, **kwargs)
                if (autocommit):
                    connection.commit ()
                catalog.idle (pool_name, connection)
                return result
            except:
                try:
                    connection.rollback ()
                    catalog.idle (pool_name, connection)
                except:
                    cherrypy.log.error (
                        'Error in temporary pool "{}" at rollback'.format (pool_name),
                        context = 'TEMPDB',
                        traceback = True,
                        severity = logging.ERROR
                    )
                    catalog.remove (pool_name, connection)
                raise
        return _wrapped
    return _wrap


_default_driver = 'pgsql'
_drivers = {
    'pgsql': 'PgSql',
    'mysql': 'MySql',
    'sqlite': 'Sqlite',
    'mongodb': 'MongoDb'
}
def get_driver (params):
    name = params.get ('driver', _default_driver).lower ()
    if name not in _drivers:
        raise KeyError ('Unknown DB driver')
    Driver = getattr (importlib.import_module ('cherrybase.db.drivers.%s' % name), _drivers [name])
    defaults = Driver.defaults.copy ()
    defaults.update ({
        'min_connections': 1,
        'max_connections': 10,
        'timeout': 0
    })
    return Driver (**{param: params.get (param, value) for param, value in defaults.iteritems ()})


class TempDBLibrary (rco.Namespace):
    
    _re_schema = re.compile ('[a-z_][a-z_\d]*', re.I)
    
    @rpc.expose
    def append (self, schema, params):
        '''Создать пул подключений к временной базе данных
        с именем schema с заданными параметрами.

        :param schema: Имя схемы, а заодно и имя пула
        :param params: dict с параметрами. Смотри defaults в драйверах БД cherrybase
        '''
        if schema in catalog:
            raise KeyError ('Duplicate schema name')
        if not self._re_schema.match (schema):
            raise NameError ('Bad schema name')
        catalog [schema] = get_driver (params)
    
    @rpc.expose
    def remove (self, schema):
        '''Удалить пул подключений к временной базе данных с именем schema.
        Если кто-то этими подключениями пользуется - будет ай как нехорошо.

        :param schema: Имя пула
        '''
        del catalog [schema]
        
