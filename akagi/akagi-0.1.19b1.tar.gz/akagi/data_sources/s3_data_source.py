import hashlib

from akagi.data_source import DataSource
from akagi.data_file_bundles import S3DataFileBundle, LocalDataFileBundle
from akagi.iterator import FileFormat


class S3DataSource(DataSource):
    '''S3DataSource replesents a set of files on Amazon S3 bucket.
    '''

    @classmethod
    def for_prefix(cls, bucket_name, prefix, file_format=FileFormat.BINARY, no_cache=False):
        return S3DataSource(bucket_name, prefix=prefix, keys=None, file_format=file_format, no_cache=no_cache)

    @classmethod
    def for_keys(cls, bucket_name, keys, file_format=FileFormat.BINARY, no_cache=False):
        return S3DataSource(bucket_name, prefix=None, keys=keys, file_format=file_format, no_cache=no_cache)

    @classmethod
    def for_key(cls, bucket_name, key, file_format=FileFormat.BINARY, no_cache=False):
        return S3DataSource.for_prefix(bucket_name, prefix=None, keys=[key],
                                       file_format=file_format, no_cace=no_cache)

    def _setup_bundle(self):
        self.bundle = S3DataFileBundle(self._bucket_name, self._prefix, self._keys, self._file_format)

        if not self._no_cache:
            self.save()
            self.bundle = LocalDataFileBundle(self._local_cache_dir, self._file_format)

    def __init__(self, bucket_name, prefix=None, keys=None, file_format=FileFormat.BINARY, no_cache=False):
        self._file_format = file_format
        self._bucket_name = bucket_name
        self._keys = keys
        self._prefix = prefix
        self._no_cache = no_cache

        if self.exists_local() and not self._no_cache:
            self.bundle = LocalDataFileBundle(self._local_cache_dir, self._file_format)
        else:
            self.bundle = None

    def __iter__(self):
        if self.bundle is None:
            self._setup_bundle()

        return iter(self.bundle)

    @property
    def _hex_hash(self):
        sig = self._bucket_name
        if self._prefix:
            sig = '$$'.join([sig, self._prefix])

        if self._keys:
            sig.append('$$'.join(self._keys))

        return hashlib.sha256(sig.encode('utf-8')).hexdigest()
