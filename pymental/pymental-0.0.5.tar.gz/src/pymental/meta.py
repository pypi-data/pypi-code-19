import xmltodict
from six import add_metaclass

from pymental.fields import BaseField, SKIP, format_attrs


class MetaModel(type):
    def __new__(cls, cls_name, bases, attrs):
        remaining_attrs = {}

        fields = {}

        for base in bases:
            fields.update(getattr(base, '_fields', {}))

        for attr, value in attrs.items():
            if isinstance(value, BaseField):
                fields[attr] = value
            else:
                remaining_attrs[attr] = value

        remaining_attrs['_fields'] = fields
        return super(MetaModel, cls).__new__(cls, cls_name, bases, remaining_attrs)


# base for our custom objects (Job, Input, Profile, etc.) aka models.Model
@add_metaclass(MetaModel)
class Model(object):

    _tag = NotImplementedError
    _attributes = {}

    def __init__(self, **kwargs):
        for name, field in self._fields.items():
            setattr(self, name, kwargs.get(name, field.default))

    @classmethod
    def from_dict(cls, node):

        instance = cls()

        if not isinstance(node, list):
            attrs = format_attrs(node)
            setattr(instance, '_attributes', attrs)

        for name, field in instance._fields.items():
            value = field.value(node)
            setattr(instance, name, value)

        return instance

    def to_dict(self):
        root = {}
        for name, field in self._fields.items():
            value = getattr(self, name)
            if value is not SKIP:
                root[field._tag] = field.to_dict(value)
        return root

    @classmethod
    def parse(self, xml):
        return self.from_dict(xmltodict.parse(xml)[self._tag])

    def unparse(self, pretty=True):
        root = {self._tag: self.to_dict()}
        attrs = {'@{}'.format(k): v for k, v in self._attributes.items()}
        root[self._tag].update(attrs)
        return xmltodict.unparse(root, pretty=pretty)

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)
