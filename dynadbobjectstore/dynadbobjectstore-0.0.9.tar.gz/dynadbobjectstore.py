import logging
import json
from boto.dynamodb2.table import Table
from boto.dynamodb2.fields import HashKey


log = logging.getLogger(__name__)


class DynaDBObjectStoreException(Exception):
    pass

class InvalidParameterException(DynaDBObjectStoreException):
    pass


class ObjectStore(object):

    def __init__(self, aws_conn, table_name, to_string=json.dumps, from_string=json.loads):
        if not aws_conn or '.DynamoDBConnection' not in str(type(aws_conn)):
            raise InvalidParameterException("Expecting an instance of boto DynamoDB connection")
        self.aws_conn = aws_conn
        self.table_name = table_name
        self.to_string = to_string
        self.from_string = from_string
        self.table = None

    def create_table(self):
        """Create the DynamoDB table used by this ObjectStore, only if it does
        not already exists.
        """

        all_tables = self.aws_conn.list_tables()['TableNames']

        if self.table_name in all_tables:
            log.info("Table %s already exists" % self.table_name)
        else:
            log.info("Table %s does not exist: creating it" % self.table_name)

            self.table = Table.create(
                self.table_name,
                schema=[
                    HashKey('key')
                ],
                throughput={
                    'read': 10,
                    'write': 10,
                },
                connection=self.aws_conn,
            )

    def _get_table(self):
        if not self.table:
            self.table = Table(self.table_name, connection=self.aws_conn)

    def put(self, key, value):
        """Marshall the python object given as 'value' into a string, using the
        to_string marshalling method passed in the constructor, and store it in
        the DynamoDB table under key 'key'.
        """
        self._get_table()
        s = self.to_string(value)
        log.debug("Storing in key '%s' the object: '%s'" % (key, s))
        self.table.put_item(
            data={
                'key': key,
                'value': s,
            },
            overwrite=True
        )

    def get(self, key):
        """Get the string representation of the object stored in DynamoDB under this key,
        convert it back to an object using the 'from_string' unmarshalling method passed
        in the constructor and return the object. Return None if no object found.
        """
        self._get_table()
        s = self.table.get_item(key=key)
        log.debug("Retrieved from key '%s' the object: '%s'" % (key, s['value']))
        return self.from_string(s['value'])

    def delete(self, key):
        """If this key exists, delete it"""
        self._get_table()
        self.table.delete_item(key=key)
        log.debug("Deleted item at key '%s'" % (key))
