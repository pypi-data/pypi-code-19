from __future__ import absolute_import, print_function, unicode_literals

import io
import base64
import googleapiclient.discovery

from retrying import retry

from dojo_beam.transform import BeamTransform
from dojo_google.auth import GoogleCloudAuth


def if_timeout_error(e):
    return 'timeout: timed out' in str(e)


class BeamGoogleStorageFileContentsSource(BeamTransform):

    def process(self, row):
        with GoogleCloudAuth(self.secrets['connection']):
            service = googleapiclient.discovery.build('storage', 'v1')
            return [self._extract_contents(service, row), ]

    @retry(wait_exponential_multiplier=1000,
           wait_exponential_max=10000,
           stop_max_delay=32000,
           retry_on_exception=if_timeout_error)
    def _extract_contents(self, service, key):
        file = io.BytesIO()
        req = service.objects().get_media(bucket=key['bucket'], object=key['name'])
        downloader = googleapiclient.http.MediaIoBaseDownload(file, req)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            # print("Download {}%.".format(int(status.progress() * 100)))
        file.seek(0)
        contents = file.read()
        file.close()
        return self._build_row(key, contents)

    def _build_row(self, key, contents):
        return {
            'bucket': key['bucket'],
            'name': key['name'],
            'content_bytes': base64.b64encode(contents)
        }
