import re
import boto3

from datetime import datetime

from akagi.iterator import Iterator, FileFormat
from akagi.data_files.s3_data_file import S3DataFile
from akagi.data_file_bundle import DataFileBundle
from akagi.log import logger
from akagi.utils import normalize_path


class S3DataFileBundle(DataFileBundle):
    def __init__(self, bucket_name, prefix=None, keys=None, file_format=FileFormat.CSV):
        self.bucket_name = bucket_name
        self.prefix = normalize_path(prefix)
        self.keys = keys

        if self.prefix is None and self.keys is None:
            raise Exception("Either prefix or keys must be set.")

        self.file_format = file_format
        self.iterator_class = Iterator.get_iterator_class(file_format)

        self.__s3 = None

    @property
    def data_files(self):
        if self.prefix is not None:
            return [S3DataFile(obj, self.iterator_class)
                    for obj in self._bucket.objects.filter(Prefix=self.prefix)]
        else:
            return [S3DataFile(self._bucket.Object(key), self.iterator_class)
                    for key in self.keys]

    def clear(self):
        for obj in self._bucket.objects.filter(Prefix=self.prefix):
            logger.debug("Deleting intermediate object on s3: %(key)s" % ({"key": obj.key}))
            obj.delete()

    @property
    def _bucket(self):
        return self._s3.Bucket(self.bucket_name)

    @property
    def _s3(self):
        if self.__s3 is None:
            self.__s3 = boto3.resource('s3')

        return self.__s3
