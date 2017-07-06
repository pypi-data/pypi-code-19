#pylint: disable=too-many-ancestors
import logging
import re

import sqlalchemy
import sqlalchemy.exc

LOGGER = logging.getLogger(__name__)

class RecordNotFound(Exception):
    pass

class TransactionError(Exception):
    pass

class ThreadError(Exception):
    pass

class SavepointError(TransactionError):
    def __init__(self, **kwargs): # pylint: disable=unused-argument
        super().__init__()

class DataError(sqlalchemy.exc.DataError):
    pass

class ValueTooLongError(DataError):
    def __init__(self, column_type, statement, params, orig, connection_invalidated):
        self.column_type = column_type
        super().__init__(statement, params, orig, connection_invalidated)

class InvalidUUIDError(DataError):
    pass

class IntegrityError(sqlalchemy.exc.IntegrityError):
    pass

class DuplicateKeyError(IntegrityError):
    def __init__(self, constraint_name, column_name, value, statement, params, orig, connection_invalidated): # pylint: disable=too-many-arguments
        self.constraint_name = constraint_name
        self.column_name = column_name
        self.value = value
        super().__init__(statement, params, orig, connection_invalidated)

class ForeignKeyError(IntegrityError):
    def __init__(self, column_name, constraint_name, referenced_table, table_name, value, statement, params, orig, connection_invalidated): # pylint: disable=too-many-arguments
        self.column_name        = column_name
        self.constraint_name    = constraint_name
        self.referenced_table   = referenced_table
        self.table_name         = table_name
        self.value              = value
        super().__init__(statement, params, orig, connection_invalidated)

class CheckConstraintError(IntegrityError):
    def __init__(self, constraint_name, row_values, table_name, statement, params, orig, connection_invalidated): # pylint: disable=too-many-arguments
        self.constraint_name    = constraint_name
        self.row_values         = row_values
        self.table_name         = table_name
        super().__init__(statement, params, orig, connection_invalidated)

ERRORS = {
    r'badly formed hexadecimal UUID string'                                                 : InvalidUUIDError,
    r'invalid input syntax for uuid'                                                        : InvalidUUIDError,
    r'value too long for type (?P<column_type>.*)\n'                                        : ValueTooLongError,
    (r'duplicate key value violates unique constraint "(?P<constraint_name>.*)"\n'
     r'DETAIL:  Key \((?P<column_name>.*)\)=\((?P<value>.*)\) already exists.\n')           : DuplicateKeyError,
    (r'insert or update on table "(?P<table_name>.*)" violates foreign key constraint '
     r'"(?P<constraint_name>.*)"\n'
     r'DETAIL:  Key \((?P<column_name>.*)\)=\((?P<value>.*)\) is not present in table '
     r'"(?P<referenced_table>.*)".\n')                                                      : ForeignKeyError,
    (r'new row for relation "(?P<table_name>.*)" violates check '
     r'constraint "(?P<constraint_name>.*)"\n'
     r'DETAIL:  Failing row contains (?P<row_values>.*).\n')                                : CheckConstraintError,
    r'SAVEPOINT can only be used in transaction blocks'                                     : SavepointError,
    r'ROLLBACK TO SAVEPOINT can only be used in transaction blocks'                         : SavepointError,
}
ERRORS = {re.compile(k): v for k, v in ERRORS.items()}
def parse_exception(exc):
    message = 'unknown'
    if isinstance(exc, (sqlalchemy.exc.DataError, sqlalchemy.exc.IntegrityError, sqlalchemy.exc.StatementError)):
        message = exc.orig.args[0]
    for k, v in ERRORS.items():
        match = k.match(message)
        if match:
            parameters = match.groupdict()
            for attribute in ('statement', 'params', 'orig', 'connection_invalidated'):
                if hasattr(exc, attribute):
                    parameters[attribute] = getattr(exc, attribute)
            return v(**parameters)
    LOGGER.warning("Failed to find a matching exception pattern for: %s", message)
    return exc
