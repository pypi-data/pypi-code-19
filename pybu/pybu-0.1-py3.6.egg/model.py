from pybu.fields import Field


class ModelMeta(type):
    def __new__(mcs, name, bases, attrs, **kwargs):
        cls = super().__new__(mcs, name, bases, attrs)
        fields = set()
        required = set()
        for field, value in attrs.items():
            if isinstance(value, Field):
                fields.add(field)
                value._field_name = field
                if value.required:
                    required.add(field)
        cls._fields = frozenset(fields)
        cls._required_fields = frozenset(required)
        return cls


class Model(metaclass=ModelMeta):
    def __init__(self, **kwargs):
        fields = set(kwargs.keys())

        additional = fields - self._fields
        if additional:
            raise AttributeError('Fields %r are not in model' % additional)

        required = self._required_fields - fields
        if required:
            raise AttributeError('Fields %r are requiered' % required)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        ret = {}
        for field in self._fields:
            value = getattr(self, field)
            if isinstance(value, Model):
                value = value.to_dict()
            elif isinstance(value, (tuple, list)):
                collection = []
                for element in value:
                    if isinstance(element, Model):
                        element = element.to_dict()
                    collection.append(element)
                value = collection
            ret[field] = value

        return ret

    def __eq__(self, other):
        assert isinstance(other, Model)
        return all(getattr(self, f) == getattr(other, f) for f in self._fields)
