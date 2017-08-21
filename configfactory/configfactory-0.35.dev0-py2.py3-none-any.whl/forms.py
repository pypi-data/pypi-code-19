from django.core.exceptions import ValidationError
from django.forms import fields
from django.utils.html import format_html

from configfactory.exceptions import JSONEncodeError
from configfactory.utils import json_dumps, json_loads


def html_params(**kwargs):
    params = []
    for k, v in sorted(kwargs.items()):
        if k in ('class_', 'class__', 'for_'):
            k = k[:-1]
        elif k.startswith('data_'):
            k = k.replace('_', '-', 1)
        if v is True:
            params.append(k)
        elif v is False:
            pass
        else:
            params.append('%s=%s' % (str(k), format_html(v)))
    return ' '.join(params)


class JSONFormField(fields.CharField):

    def to_python(self, value):
        if isinstance(value, str):
            try:
                return json_loads(value)
            except JSONEncodeError:
                raise ValidationError("Enter valid JSON")
        return value

    def clean(self, value):
        if not value and not self.required:
            return None
        try:
            return super().clean(value)
        except TypeError:
            raise ValidationError("Enter valid JSON")

    def prepare_value(self, value):
        if isinstance(value, dict):
            return json_dumps(value, indent=4)
        return value
