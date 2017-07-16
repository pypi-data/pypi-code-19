# coding: utf-8


class BaseStructure(object):
    __slots__ = []

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented

        if self.__class__ != other.__class__:
            return False

        return all([
            getattr(self, x) == getattr(other, x)
            for x in self.__slots__
        ])

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(tuple(
            getattr(self, x) for x in self.__slots__
        ))

    def to_primitive(self, context=None):
        fields = ((key, getattr(self, key)) for key in self.__slots__)
        return {
            key: self._to_primitive(value, context)
            for key, value in fields
        }

    @staticmethod
    def _to_primitive(instance, context):
        if hasattr(instance, 'to_primitive'):
            return instance.to_primitive(context)
        elif hasattr(instance, 'isoformat'):
            return instance.isoformat()
        else:
            return instance
