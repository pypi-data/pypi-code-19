import json
import pathlib
import sys
import time
from types import MappingProxyType

import boto3

from .. import interface


class ConstantInputter(interface.Inputter):
    def __init__(self, value, metadata):
        self.value = value
        self.metadata = metadata

    def read(self):
        return interface.Context(self.value, **self.metadata)


class StdinInputter(interface.Inputter):
    def read(self):
        return interface.Context(sys.stdin.read())


class FileInputter(interface.Inputter):
    def __init__(self, filepath):
        self.path = pathlib.Path(filepath).resolve()

    def read(self):
        return interface.Context(self.path.open().read())


class SQSS3Inputter(interface.Inputter):

    def __init__(self, bucket_name, queue_name,
                 *,
                 s3_config=MappingProxyType({}),
                 sqs_config=MappingProxyType({})):
        s3 = boto3.resource('s3', **s3_config)
        sqs = boto3.resource('sqs', **sqs_config)
        bucket = s3.Bucket(bucket_name)
        queue = sqs.get_queue_by_name(QueueName=queue_name)
        self.bucket = bucket
        self.queue = queue
        self.message = None

    def read(self):
        message = self.__read_sqs()
        body, meta = self.__read_s3(message)
        return interface.Context(body, **meta)

    def __read_sqs(self):
        if self.message is not None:
            return self.message

        messages = list(self.queue.receive_messages())
        while not messages:
            time.sleep(5)
            messages = list(self.queue.receive_messages())

        message = messages[0]
        self.message = message
        return message

    def __read_s3(self, message):
        j = json.loads(message.body)
        obj = self.bucket.Object(j['s3_body'])
        metadata = j['metadata']
        response = obj.get()
        return response['Body'].read(), metadata

    def done(self):
        super().done()
        self.message.delete()


__all__ = ['ConstantInputter', 'SQSS3Inputter']
