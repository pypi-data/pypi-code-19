from pybu.exceptions import FieldTypeError


def type_validator(type_):
    def _validator(field, value):
        if not isinstance(value, type_):
            raise FieldTypeError(
                f'{repr(value)} is not instance of {repr(type_)}')

    return _validator


def tuple_type_validator():
    tuple_validator = type_validator(tuple)

    def _validator(field, value):
        tuple_validator(field, value)
        elem_type = field._elem_type
        if elem_type is not None:
            for i, elem in enumerate(value):
                if not isinstance(elem, elem_type):
                    raise FieldTypeError(
                        f'{repr(value)}#{i} '
                        f'is not instance of {repr(elem_type)}')
    return _validator

class Field:
    validator = None

    def __init__(self, default=None, required=False):
        self._field_name = None
        self._default = default
        self.required = required

    def _get_field_name(self, instance):
        assert self._field_name
        return f"_{self._field_name}_{id(instance)}"

    def normalize(self, value):
        return value

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return getattr(
                instance, self._get_field_name(instance), self._default)

    def __set__(self, instance, value):
        if self.validator is not None:
            self.validator(value)
        value = self.normalize(value)
        setattr(instance, self._get_field_name(instance), value)


class Str(Field):
    validator = type_validator(str)


class Int(Field):
    validator = type_validator(int)


class Float(Field):
    validator = type_validator(float)


class Bool(Field):
    validator = type_validator(bool)

    def normalize(self, value):
        return bool(value)


class Dict(Field):
    validator = type_validator(dict)


class Tuple(Field):
    validator = tuple_type_validator()

    def __init__(self, type_=None):
        self._elem_type = type_
        super(Tuple, self).__init__(required=True)
