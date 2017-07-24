from elasticsearch_dsl import field, analyzer

__base_fields = (
    'Object', 'String', 'Text', 'Date', 'Keyword', 'Nested',
    'InnerObjectWrapper',
    'Float', 'Double', 'Byte', 'Short', 'Integer', 'Long', 'Boolean',
    'Ip', 'Attachment',
    'GeoPoint', 'GeoShape',
    'Completion',
)


html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)


class FlexField(object):
    def __init__(self, attr=None, *a, **kwa):
        self._model_attr = attr
        super(FlexField, self).__init__(*a, **kwa)


class HTMLField(FlexField, field.Text):
    def __init__(self, *a, **kwa):
        kwa['analyzer'] = html_strip
        super(HTMLField, self).__init__(*a, **kwa)


def __make_field(fieldname):
    class_name = fieldname + 'Field'
    base = getattr(field, fieldname)
    klass = type(class_name, (FlexField, base), {'__doc__': base.__doc__})
    return klass

__all__ = ['FlexField']
for __field in __base_fields:
    fclass = __make_field(__field)
    globals()[fclass.__name__] = fclass
    __all__.append(fclass.__name__)
