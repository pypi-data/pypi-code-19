import hashlib
import io
import json
import logging
import os
import pathlib
import requests
import rfc6266
import uuid

def _calculate_sha1(in_file):
    m = hashlib.sha1()
    for chunk in iter(lambda: in_file.read(8192), b''):
        m.update(chunk)
    return m.hexdigest()

class Upload:
    """Start an Upload session.

    :param str server_url: Website to upload to. For example:
        ``https://www.overviewdocs.com``
    :param str api_token: String from
        https://www.overviewdocs.com/documentsets/XXXX/api-tokens
    """

    def __init__(self, server_url, api_token, logger=None):
        if logger is None:
            logger = logging.getLogger('{}.Upload'.format(__name__))

        self.server_url = server_url
        self.api_token = api_token
        self.logger = logger
        self.n_uploaded = 0

    def _request(self, method, path, **kwargs):
        url = '{}{}'.format(self.server_url, path)
        self.logger.debug('%s %s', method, url)

        # We need a "nested" dict.update(), for the headers argument. If the
        # caller specifies headers, we want them to override our defaults.
        request_headers = {
            'X-Requested-With': 'overview_upload',
        }
        if 'headers' in kwargs:
            request_headers.update(kwargs['headers'])

        request_kwargs = {
                'auth': (self.api_token, 'x-auth-token'),
        }
        request_kwargs.update(kwargs)
        request_kwargs['headers'] = request_headers

        return requests.request(method, url, **request_kwargs)

    def clear_previous_upload(self):
        """Remove any previously uploaded files from the server.

        If you *don't* call this, then when you ``finish()`` you may find
        Overview adds files you uploaded sometime in the past and then forgot
        about.
        """
        self.logger.info('Clearing previous uploads…')
        r = self._request('DELETE', '/api/v1/files')
        r.raise_for_status()

    def send_directory(self, dirname, skip_unhandled_extension=True, skip_duplicate=True, metadata=None):
        """Upload all files in a directory to the Overview server.

        If ``skip_duplicate == False``, then files will be streamed to the
        server. Otherwise, this method will cache each file in memory during
        upload.

        :param str dirname: Directory to upload.
        :param bool skip_unhandled_extension: if ``True`` (the default), do not
            upload files when Overview doesn't support their filename extensions
            (for instance, ``".dbf"``).
        :param bool skip_duplicate: if ``True`` (the default), do not upload a
            file if ``api_token`` points to a document set that already contains a
            file whose sha1 hash is identical to this file's. Files that have been
            sent without a call to ``finish()`` will not be included in the check.
            If ``False``, stream files instead of caching them.
        :param dict metadata: Metadata to set on every document, or ``None``.
            The document set should have a metadata schema that corresponds to
            this document's metadata (or you can set the schema later).
        """
        for path in pathlib.Path(dirname).glob('**/*'):
            filename = str(path.relative_to(dirname)) # visible on the server

            # Don't upload hidden files (e.g., ".DS_Store" on Mac OS)
            if filename[0] == '.' or '/.' in filename or '\\.' in filename:
                continue

            if path.is_file():
                self.send_path_if_conditions_met(
                    path,
                    filename,
                    skip_unhandled_extension=skip_unhandled_extension,
                    skip_duplicate=skip_duplicate,
                    metadata=metadata
                )

    def send_path_if_conditions_met(self, path, filename, skip_unhandled_extension=True, skip_duplicate=True, metadata=None):
        """Upload the file at the specified Path to the Overview server.

        The file will be streamed: that is, the script does not risk running out
        of memory.

        :param pathlib.Path path: absolute or relative pathlib.Path pointing
            to the document.
        :param str filename: filename Overview should use.
        :param bool skip_unhandled_extension: -- if ``True`` (the default), do
            not upload this file if Overview doesn't support its filename
            extension (for instance, ``".dbf"``).
        :param bool skip_duplicate: if ``True`` (the default), do not upload
            this file if your api_token points to a document set that already
            contains a file whose sha1 hash is identical to this file's. Files
            that have been sent but not finish()ed will not be included in the
            check.
        :param dict metadata: Metadata to set on the document, or ``None``.
            The document set should have a metadata schema that corresponds to
            this document's metadata (or you can set the schema later).
        """
        n_bytes = path.stat().st_size

        sha1 = None
        if skip_duplicate:
            # we need to stream the file to calculate sha1, and then we need
            # to stream it again to send it to the server. Do that by
            # opening the file twice: the alternative is to read the entire
            # file into memory, which can be huge.
            with path.open('rb') as in_file:
                sha1 = _calculate_sha1(in_file)

        with path.open('rb', buffering=8192) as in_file:
            self.send_file_if_conditions_met(
                in_file,
                filename,
                n_bytes=n_bytes,
                skip_unhandled_extension=skip_unhandled_extension,
                skip_duplicate=skip_duplicate,
                metadata=metadata,
                sha1=sha1
            )

    def send_file_if_conditions_met(self, in_file, filename, n_bytes=None, skip_unhandled_extension=True, skip_duplicate=True, metadata=None, sha1=None):
        """Upload a file to the Overview server.

        If ``n_bytes is None or (skip_duplicate == True and sha1 is None)``,
        then ``in_file`` will be cached in memory. Otherwise, it will be
        streamed to the server, saving memory.

        :param io.BytesIO in_file: BytesIO containing the document.
        :param str filename: Filename to set in Overview.
        :param int n_bytes: Exact file size (or `None` to auto-calculate).
            Supply this and ``sha1`` (if applicable) to stream ``in_file`` to
            the server instead of caching it in memory.
        :param bool skip_unhandled_extension: if ``True`` (the default), do not
            upload this file if Overview doesn't support its filename extension
            (for instance, ``".dbf"``).
        :param bool skip_duplicate: if ``True`` (the default), do not upload
            this file if your api_token points to a document set that already
            contains a file whose sha1 hash is identical to this file's. Files
            that have been sent without a call to ``finish()`` will not be
            included in the check.
        :param dict metadata: Metadata to set on the document, or ``None``.
            The document set should have a metadata schema that corresponds to
            this document's metadata (or you can set the schema later).
        :param str sha1: SHA1 hash:to use in ``skip_duplicate()`` check, or
            ``None`` to calculate on the fly. If you set this and ``n_bytes``,
            this method will stream the file contents instead of caching them
            in memory.
        """
        if skip_unhandled_extension:
            # We go by filename, with a blacklist we know Overview doesn't handle (yet)
            path, ext = os.path.splitext(filename)
            if ext.lower() in ['.zip', '.msg', '.gif', '.jpg', '.png', '.tiff', '.tif', '.dbf']:
                self.logger.info('Skipping %s, Overview does not handle this format', filename)
                return

        if skip_duplicate:
            if sha1 is None:
                # Cache in_file bytes in memory so we can read it twice: once in
                # is_file_already_in_document_set(), and once below.
                in_file = io.BytesIO(in_file.read())
                sha1 = _calculate_sha1(in_file)
                in_file.seek(0)

            if self.is_file_already_in_document_set(in_file, sha1):
                self.logger.info('Skipping %s, already on server', filename)
                return

        if n_bytes is None:
            # Cache in_file bytes in memory so we can read it twice: once 
            # here, once below
            in_file = io.BytesIO(in_file.read())
            n_bytes = in_file.getbuffer().nbytes

        server_path = '/api/v1/files/{}'.format(uuid.uuid4())
        headers = {
            'Content-Disposition': rfc6266.build_header(filename),
            'Content-Length': str(n_bytes),
        }
        if metadata:
            headers['Overview-Document-Metadata-JSON'] = json.dumps(metadata, ensure_ascii=True)

        self.logger.info('Uploading %s…', filename)
        r = self._request('POST', server_path, headers=headers, data=in_file)
        r.raise_for_status()
        self.n_uploaded += 1

    def is_file_already_in_document_set(self, in_file, sha1=None):
        """Return True iff the document set contains an identical file.

        This works by calculating the SHA1 and asking Overview whether it's been
        seen before in our document set. Files sent without a call to
        ``finish()`` will not be included in this check.

        :param io.BytesIO in_file: bytes to upload to Overview.
        :param str sha1: if set, assume the given SHA1 hash instead of computing
            it by reading the file. If ``None`` (the default), then ``in_file``
            will be read completely.
        """
        if sha1 is None:
            sha1 = _calculate_sha1(in_file)

        r = self._request('HEAD', '/api/v1/document-sets/files/{}'.format(sha1))

        if r.status_code == 204:
            return True
        elif r.status_code == 404:
            return False
        else:
            r.raise_for_status()

    def finish(self, lang='en', ocr=True, split_by_page=False):
        """Adds sent files to the document set.

        :param str lang: ISO language code for Overview's analysis (default is
            ``"en"``)
        :param bool ocr: if ``True`` (the default), tell Overview to read text
            from PDF pages that contain only images.
        :param bool split_by_page: if ``True``, tell Overview to create a
            document per page of the input file. (This only applies to PDFs and
            LibreOffice-compatible documents.) If ``False`` (the default), tell
            Overview to create one document per uploaded file.
        """
        if self.n_uploaded == 0:
            self.logger.info('No files uploaded')
            return

        # http://docs.overviewproject.apiary.io/#reference/files/finish-uploading-files/add-files-to-document-set?console=1
        self.logger.info('Finishing…')
        r = self._request('POST', '/api/v1/files/finish', json={
            'lang': lang,
            'ocr': ocr,
            'split_documents': split_by_page,
        })
        r.raise_for_status()
        self.logger.info(
            'Finished uploading %d file(s). Browse to %s/documentsets to watch progress',
            self.n_uploaded,
            self.server_url
        )
