import hashlib
import json
import sys
from types import MappingProxyType

import boto3
import sqlalchemy
from sqlalchemy.ext.automap import automap_base

from .. import interface


class StdoutOutputter(interface.Outputter):
    def write(self, value, *, context=None):
        if context is not None:
            metadata = context.metadata
        else:
            metadata = {}

        if isinstance(value, bytes):
            try:
                value = value.decode('UTF-8')
            except Exception:
                pass
        print(value, file=sys.stdout)


class SQSS3Outputter(interface.Outputter):

    def __init__(self, bucket_name, queue_name,
                 *,
                 s3_config=MappingProxyType({}),
                 sqs_config=MappingProxyType({})):
        super().__init__()
        s3 = boto3.resource('s3', **s3_config)
        sqs = boto3.resource('sqs', **sqs_config)
        bucket = s3.Bucket(bucket_name)
        queue = sqs.get_queue_by_name(QueueName=queue_name)
        self.bucket = bucket
        self.queue = queue

    def write(self, value, *, context=None):
        bucket = self.bucket
        queue = self.queue
        encoding = 'UTF-8'
        if context is not None:
            metadata = context.metadata
        else:
            metadata = {}
        if isinstance(value, str):
            value = value.encode(encoding)

        name = hashlib.sha256(value).hexdigest()
        obj = bucket.Object(name)
        obj.put(
            Body=value,
            ContentEncoding=encoding,
            ContentType='text/plain',
        )
        j = json.dumps({'s3_body': obj.key, 'metadata': metadata})
        queue.send_message(MessageBody=j)


class SQLOutputter(interface.Outputter):
    def __init__(self, url, table):
        self.engine = sqlalchemy.create_engine(url)
        self.table = table
        metadata = sqlalchemy.MetaData()
        metadata.reflect(self.engine, only=[table])
        Base = automap_base(metadata=metadata)
        Base.prepare()
        self.query = metadata.tables[table].insert()

    def write(self, value, *, context=None):
        j = json.loads(value)
        self.engine.execute(self.query.values(j))


__all__ = ['StdoutOutputter', 'SQSS3Outputter', 'SQLOutputter']
