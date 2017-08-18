from __future__ import absolute_import, print_function, unicode_literals

import os
import json
import io
import apache_beam as beam
import googleapiclient

from googleapiclient import discovery
from apache_beam.io import ReadFromText, WriteToText, WriteToTFRecord

from dojo.storage import Storage

from .transform import ConvertTo
from .util import flatten


class BeamStorage(Storage):

    def read(self, path_or_source):
        if isinstance(path_or_source, (str, unicode)):
            path = path_or_source
            source = None
        else:
            path = None
            source = path_or_source
        p = self.dataset.pipeline
        if source:
            rows = (p | 'read ' + str(source) >> beam.io.Read(source))
        else:
            input_uri = self.as_uri(path)
            rows = (p | 'read ' + input_uri >> ReadFromText(str(input_uri)))
        return rows

    def write(self, path, rows, format='json'):
        extensions = {
            'json': '.json',
            'csv': '.csv',
            'tf': '.tfrecord.gz'
        }
        writers = {
            'json': WriteToText,
            'csv': WriteToText,
            'tf': WriteToTFRecord
        }
        extension = extensions.get(format)
        writer = writers[format]
        output_uri = self.as_uri(path)
        rows = rows | 'convert ' + output_uri + ' ' + format >> beam.ParDo(ConvertTo(format))
        rows | 'write ' + output_uri + ' ' + format >> writer(str(output_uri), file_name_suffix=extension)
        return rows

    def list_keys(self, prefix):
        raise NotImplementedError()


class BeamLocalFileStore(BeamStorage):

    def as_uri(self, path):
        if 'prefix' in self.config:
            path = os.path.join(self.config['prefix'], path)
        return path

    def list_keys(self, prefix):
        if 'prefix' in self.config:
            prefix = os.path.join(self.config['prefix'], prefix)
        if os.path.isfile(prefix):
            dirname = os.path.dirname(prefix)
        else:
            dirname = prefix
        if not os.path.isdir(dirname):
            return []
        return os.listdir(dirname)


class BeamGoogleStorageStore(BeamStorage):

    def setup(self):
        keyfile_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if keyfile_path and not os.path.isfile(keyfile_path):
            with open(keyfile_path, 'w') as f:
                json.dump(self.secrets['connection'], f)
        self.service = discovery.build('storage', 'v1')

    def write(self, path, rows, format='json'):
        return super(BeamGoogleStorageStore, self).write(str(path), rows, format=format)

    def list_keys(self, prefix):
        req = self.service.objects().list(bucket=self.config['bucket'], prefix=prefix, delimiter='/')
        keys = []
        while req:
            resp = req.execute()
            keys += resp.get('prefixes', [])
            keys += [key['name'] for key in resp.get('items', [])]
            req = self.service.objects().list_next(req, resp)
        return keys

    def as_uri(self, path):
        return '%s://%s/%s' % (self.config['protocol'], self.config['bucket'], path)

    def read_file(self, path, file=None):
        if file is None:
            return self._read_rows(path)
        elif isinstance(file, io.BytesIO) or hasattr(file, 'read'):
            return self._read_file(path, file)
        else:
            raise ValueError('unsupported type to read file from storage', type(file))

    def write_file(self, path, file_or_rows, format='json'):
        if isinstance(file_or_rows, (list, tuple)):
            self._write_rows(path, file_or_rows, format=format)
        elif isinstance(file_or_rows, io.BytesIO) or hasattr(file_or_rows, 'read'):
            self._write_file(path, file_or_rows)
        else:
            raise ValueError('unsupported type to write file to storage', type(file_or_rows))

    def _read_rows(self, key):
        file = io.BytesIO()
        req = self.service.objects().get_media(bucket=self.config['bucket'], object=key)
        downloader = googleapiclient.http.MediaIoBaseDownload(file, req)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            # print("Download {}%.".format(int(status.progress() * 100)))
        file.seek(0)
        rows = file.read().decode('utf-8').split('\n')
        file.close()
        return rows

    def _read_file(self, key, to_file):
        req = self.service.objects().get_media(bucket=self.config['bucket'], object=key)
        downloader = googleapiclient.http.MediaIoBaseDownload(to_file, req)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            # print("Download {}%.".format(int(status.progress() * 100)))
        to_file.seek(0)
        return to_file

    def _write_file(self, path, file):
        req = self.service.objects()\
                          .insert(bucket=self.config['bucket'],
                                  body={'name': path},
                                  media_body=googleapiclient.http.MediaIoBaseUpload(file, 'text/plain'))
        req.execute()

    def _write_rows(self, path, rows, format='json'):
        rows = flatten([ConvertTo(format).process(row) for row in rows])
        f = io.BytesIO('\n'.join(rows).encode('utf-8'))
        req = self.service.objects()\
                          .insert(bucket=self.config['bucket'],
                                  body={'name': path},
                                  media_body=googleapiclient.http.MediaIoBaseUpload(f, 'text/plain'))
        req.execute()


class BeamS3Store(BeamStorage):
    pass
