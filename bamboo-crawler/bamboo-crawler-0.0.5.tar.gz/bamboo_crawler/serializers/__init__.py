import json

from .. import interface


class NullSerializer(interface.Serializer):
    def serialize(self, value):
        return value


class JSONSerializer(interface.Serializer):
    def serialize(self, value):
        return json.dumps(value)


__all__ = ['NullSerializer']
