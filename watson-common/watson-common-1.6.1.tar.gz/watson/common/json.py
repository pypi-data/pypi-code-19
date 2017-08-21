# -*- coding: utf-8 -*-
import json
import inspect
from watson.common import strings


class JSONEncoder(json.JSONEncoder):
    """Extends the original JSONEncoder to allow for serializing classes.

    Example:

    .. code-block:: python

        class MyClass(object):
            attr = 'Value'

        c = MyClass()
        encoder = JSONEncoder()
        encoder.encode(c, mapping={MyClass: 'attributes': ('attr',)})
        # {"attr": "Value"}

        obj = {"date": datetime.now()}
        encode.encode(obj, mapping={datetime: lambda x: x.strftime('%d/%m/%Y')})
        # {"date": "D/M/Y"}

    """
    _mapping = None
    camelcase = False

    @property
    def mapping(self):
        if not self._mapping:
            self.mapping = {}
        return self._mapping

    @mapping.setter
    def mapping(self, mapping):
        self._mapping = mapping

    def default(self, o):
        _type = type(o)
        if inspect.isclass(_type):
            mapping = self.mapping.get(o.__class__, {})
            if isinstance(mapping, dict):
                if hasattr(o, '__iter__') and not mapping:
                    return [self.default(i) for i in o]
                return serialize(
                    o,
                    attributes=mapping.get('attributes', ()),
                    strategies=mapping.get('strategies', {}),
                    camelcase=self.camelcase)
            elif mapping:
                return mapping(o)
            else:
                return [self.default(i) for i in o]
        return json.JSONEncoder.default(self, o)

    def _camelize_attributes(self, o):
        if isinstance(o, dict):
            new_o = {}
            for attr in o:
                camelized_attr = strings.camelcase(attr, uppercase=False)
                new_o[camelized_attr] = self._camelize(o[attr])
            return new_o
        return o

    def _camelize(self, o):
        if isinstance(o, (list, tuple)):
            for i in range(len(o)):
                o[i] = self._camelize_attributes(o[i])
        return self._camelize_attributes(o)

    def encode(self, o, mapping=None, camelcase=True):
        # This is potentially a little slow, could use some improvements
        self.mapping = mapping
        self.camelcase = camelcase
        if camelcase:
            o = self._camelize(o)
        return super(JSONEncoder, self).encode(o)


def serialize(obj, attributes, strategies=None, camelcase=True, **kwargs):
    """Serializes an object into a dict suitable to be dumped to json.

    Args:
        obj (mixed): The object to serialize
        attributes (tuple): A tuple of attributes that should be serialized
        strategies (dict): Key/value pairs of strategies to deal with objects
        camelcase (bool): camelCase the attribute names
        kwargs: Passed to the strategy when it's called

    Example:

    .. code-block:: python

        class AnotherClass(object):
            name = 'Else'

        class MyClass(object):
            name = 'Something'
            complex_classes = [AnotherClass()]

        class_ = MyClass()
        d = serialize(class_, ('name', 'complex'),
                       strategies={
                            'complex_class': lambda x:
                                                serialize(y, ('name',))
                                                for y in x})
        # {'name': 'Something', 'complexClass': {'name': 'Else'}}
    """
    serialized = {}
    for attr in attributes:
        value = getattr(obj, attr)
        if value is None:
            continue
        if strategies and attr in strategies:
            value = strategies[attr](value, **kwargs)
        if camelcase:
            attr = strings.camelcase(attr, uppercase=False)
        serialized[attr] = value
    return serialized


def deserialize(obj, class_, attributes, strategies=None, snakecase=True,
                **kwargs):
    """Deserializes a dict into an object of type class_.

    Can be seen as the inverse of serialize().

    Args:
        obj (dict): The structure to deserialize
        class_ (class): The type that the object should be deserialized into
        attributes (tuple): A tuple of attributes that should be set
        strategies (dict): Key/value pairs of strategies to deal with objects
        snakecase (bool): snake_case the attribute names
        kwargs: Passed to the strategy when it's called
    """
    deserialized = class_()
    for attr in attributes:
        if snakecase:
            # camelcase the required attr
            attr = strings.camelcase(attr, uppercase=False)
        value = obj.get(attr)
        if value is None:
            continue
        if strategies and attr in strategies:
            value = strategies[attr](value, **kwargs)
        if snakecase:
            attr = strings.snakecase(attr)
        setattr(deserialized, attr, value)
    return deserialized
