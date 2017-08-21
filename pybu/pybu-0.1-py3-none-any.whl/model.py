from pybu.fields import Field, Tuple


class NoValue:
    pass


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

    @classmethod
    def from_dict(cls, dict):
        fields = {}
        for field_name in cls._fields:
            field = getattr(cls, field_name)
            value = dict.get(field_name, NoValue)
            if value is NoValue:
                if field.required:
                    raise Exception(f'Field {field_name} is required')
                else:
                    continue
            if isinstance(field, Tuple):
                model_type = field._elem_type
                if model_type is not None and issubclass(model_type, Model):
                    value = field.internal_type(
                        model_type.from_dict(v) for v in value)
                else:
                    value = field.internal_type(value)
            elif isinstance(field, Obj):
                value = field.internal_type.from_dict(value)
            else:
                value = field.internal_type(value)
            fields[field_name] = value
        return cls(**fields)

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


class Obj(Field):
    def __init__(self, type_, *args, **kwargs):
        assert issubclass(type_, Model)
        self.internal_type = type_
        super(Obj, self).__init__(*args, **kwargs)
