from collections import OrderedDict

SKIP = object()


def format_attrs(d, omit_nil=True):
    new_attrs = {k.lstrip('@'): v for k, v in d.items()
                 if k.startswith('@')}
    if omit_nil:
        new_attrs.pop('nil', None)

    return new_attrs


class BaseField(object):
    def __init__(self, tag, default=SKIP, description=None):
        self._tag = tag
        self._attributes = {}
        self.default = default
        self.description = description

    def value(self, root):
        raise NotImplementedError('def value')

    def to_dict(self, value):
        raise NotImplementedError('def to_dict')


class GenericField(BaseField):
    def value(self, tag):
        if self._tag not in tag:
            return self.default

        value = tag[self._tag]
        if isinstance(value, OrderedDict):
            attrs = format_attrs(value)
            self._attributes.update(attrs)

            if value.get('@nil'):
                value = None
            else:
                value = value.get('#text', value)

        return value

    def to_dict(self, value):
        return value if value is not SKIP else None


class RelatedField(BaseField):
    def __init__(self, tag, class_, default=SKIP):
        super(RelatedField, self).__init__(tag, default=default)
        self.class_ = class_

    def value(self, root):
        if self._tag not in root:
            return self.default
        return self.class_.from_dict(root[self._tag])

    def to_dict(self, instance):
        if instance is SKIP:
            return
        data = instance.to_dict()
        data.update(instance._attributes)
        return data


class ListField(BaseField):
    def __init__(self, tag, class_, default=SKIP):
        super(ListField, self).__init__(tag, default)
        self.class_ = class_

    def value(self, node):
        if self._tag not in node:
            return self.default

        if isinstance(node[self._tag], list):
            ret = []
            for item in node[self._tag]:
                ret.append(self.class_.from_dict(item))
            return ret
        return [self.class_.from_dict(node[self._tag])]

    def to_dict(self, instances):
        if instances is SKIP:
            return

        ret = []
        for instance in instances:
            data = instance.to_dict()
            data.update(instance._attributes)
            ret.append(data)
        return ret
