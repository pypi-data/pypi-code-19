from __future__ import unicode_literals

import MySQLdb


from dojo.vanilla.dataset import VanillaDataset


SCHEMA = {
    'type': 'object',
    'properties': {
        'type': {'type': 'string'},
        'properties': {'type': 'object', 'properties': {
        }}
    }
}


class MySQLSource(VanillaDataset):

    CONFIG = {
        'type': 'object',
        'properties': {
            'connection': {'type': 'object', 'properties': {
                'host': {'type': 'string'},
                'user': {'type': 'integer'},
                'database': {'type': 'string'}
            }},
            'sql': {'type': 'string'},
            'schema': SCHEMA
        }
    }

    SECRETS = {
        'type': 'object',
        'properties': {
            'connection': {'type': 'object', 'properties': {
                'password': {'type': 'string'}
            }}
        }
    }

    def process(self, inputs):
        conn = MySQLdb.connect(host=self.config['connection']['host'],
                               user=self.config['connection']['user'],
                               passwd=self.secrets['connection']['password'],
                               db=self.config['connection']['database'])
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(self.config['sql'])
        rows = [self._decode_row(row) for row in cursor.fetchall()]
        return rows

    def _decode_row(self, row):
        for key, value in row.items():
            if isinstance(value, (str, unicode)):
                row[key] = value.decode('latin1')
        return row
