# -*- coding: utf-8 -*-
def build_engine_string(dialect, database, driver=None, username=None, password=None, host=None, port=None):
    """ Build SQLAlchemy engine string acordind to database parameters.
        
        Args:
            dialect (str): Dialect string
            database (str): Database name or path for SQLite
        Kwargs:
            driver (str): Database driver to be used
            username (str): Database username
            password (str): Database password
            host (str): Database host
            port (str): Database port
            
        Raises:
            Exception: Raise Exception if username or password or host or port are not set for a database that
            isn't Sqlite.
    """
    if dialect != 'sqlite':
        if username is None or password is None or host is None or port is None:
            raise_msg = ("Except for sqlite database for all others username, password, host and port must be suplied:" +
                       "\nusername: %s" +\
                       "\npassword: %s" +\
                       "\nhost: %s" +\
                       "\nport: %s" )% (username, password is not None, host, port)
            raise Exception(raise_msg)

    dialect_text  = dialect
    driver_text   = '+' + driver   if driver is not None else ''
    username_text = username
    password_text = ':' + password if password is not None else ''
    host_text     = '@' + host     if host is not None else ''
    port_text     = ':' + port     if port is not None else ''
    database_text = database

    to_format_dict = {'dialect': dialect_text
                    , 'driver': driver_text
                    , 'username': username_text
                    , 'password': password_text
                    , 'host': host_text
                    , 'port': port_text
                    , 'database': database_text}
    return '%(dialect)s%(driver)s://%(username)s%(password)s%(host)s%(port)s/%(database)s' % to_format_dict