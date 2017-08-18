from __future__ import absolute_import, print_function, unicode_literals

import io
import base64
import googleapiclient.discovery

from dojo.vanilla.dataset import VanillaDataset


class GoogleStorageFiles(VanillaDataset):
    """Extract contents from keys that match the given bucket and path prefix from Google Storage"""

    OUTPUT = {
        'type': 'object',
        'properties': {
            'id': {'type': 'string'},
            'name': {'type': 'string'},
            'bucket': {'type': 'string'},
            'created_at': {'type': 'string', 'format': 'date-time'},
            'updated_at': {'type': 'string', 'format': 'date-time'},
            'size': {'type': 'number'},
            'content_type': {'type': 'string'},
            'content_bytes': {'type': 'string'}
        },
        'required': ['id', 'name', 'bucket', 'created_at', 'updated_at', 'size', 'content_type', 'content_bytes']
    }

    def process(self, inputs):
        return self._extract_keys_and_contents(self.store.config['bucket'], self.config['prefix'])

    def _extract_keys_and_contents(self, bucket, prefix):
        req = self.store.service.objects().list(bucket=bucket, prefix=prefix, delimiter='/')
        rows = []
        while req:
            resp = req.execute()
            for key in resp.get('items', []):
                row = self._build_key_row(key)
                row['bucket'] = bucket
                contents = self._extract_contents(key)
                row['content_bytes'] = base64.b64encode(contents)
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

    def _extract_contents(self, key):
        file = io.BytesIO()
        req = self.store.service.objects().get_media(bucket=key['bucket'], object=key['name'])
        downloader = googleapiclient.http.MediaIoBaseDownload(file, req)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            # print("Download {}%.".format(int(status.progress() * 100)))
        file.seek(0)
        contents = file.read()
        file.close()
        return contents
