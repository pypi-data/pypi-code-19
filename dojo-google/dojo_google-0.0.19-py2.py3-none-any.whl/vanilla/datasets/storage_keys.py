from __future__ import absolute_import, print_function, unicode_literals

import os

from dojo.vanilla.dataset import VanillaDataset


class GoogleStorageKeys(VanillaDataset):
    """Extract metadata about keys in a specific Google Storage location"""

    OUTPUT = {
        'type': 'object',
        'properties': {
            'id': {'type': 'string'},
            'name': {'type': 'string'},
            'bucket': {'type': 'string'},
            'created_at': {'type': 'string', 'format': 'date-time'},
            'updated_at': {'type': 'string', 'format': 'date-time'},
            'size': {'type': 'number'},
            'content_type': {'type': 'string'}
        },
        'required': ['id', 'name', 'bucket', 'created_at', 'updated_at', 'size', 'content_type']
    }

    def process(self, inputs):
        return self._extract_keys(self.store.config['bucket'], self.config['prefix'])

    def _extract_keys(self, bucket, prefix):
        req = self.store.service.objects().list(bucket=bucket, prefix=prefix)
        rows = []
        while req:
            resp = req.execute()
            for key in resp.get('items', []):
                row = self._build_key_row(key)
                row['bucket'] = bucket
                if 'extension' in self.config:
                    _, extension = os.path.splitext(row['name'])
                    if extension[1:].lower() == self.config['extension'].lower():
                        rows.append(row)
                else:
                    rows.append(row)
            req = self.store.service.objects().list_next(req, resp)
        return rows

    def _build_key_row(self, key):
        return {
            'id': key['id'],
            'name': key['name'],
            'created_at': key['timeCreated'],
            'updated_at': key['updated'],
            'content_type': key['contentType'],
            'size': int(key['size'])
        }
