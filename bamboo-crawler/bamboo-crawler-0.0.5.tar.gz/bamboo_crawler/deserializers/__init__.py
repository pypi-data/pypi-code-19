import gzip
import json

from .. import interface


class GzipDeserializer(interface.Deserializer):
    def deserialize(self, value):
        return gzip.decompress(value)


class JSONDeserializer(interface.Deserializer):
    def deserialize(self, value):
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        return json.loads(value)


class NullDeserializer(interface.Deserializer):
    def deserialize(self, value):
        return value


__all__ = ['GzipDeserializer', 'NullDeserializer']
