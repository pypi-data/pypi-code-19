from django import template
from django.utils.formats import get_format

from ..menu import RootMenu


DATETIME_REFS = {
    '%d': 'DD',
    '%m': 'MM',
    '%y': 'YY',
    '%Y': 'YYYY',
    '%H': 'HH',
    '%M': 'mm',
    '%S': 'ss',
    '%b': 'MMM',
    '%B': 'MMMM',
    '%a': 'DDD',
    '%A': 'DDDD',
}

register = template.Library()

def convert(s):
    for k, v in DATETIME_REFS.items():
        s = s.replace(k, v)
    return s

@register.inclusion_tag('ms_utils/tags/datepicker.html', takes_context=True)
def datepicker(context):
    date_format = get_format('DATE_INPUT_FORMATS')[0]
    datetime_format = get_format('DATETIME_INPUT_FORMATS')[0]
    request = context['request']

    return dict(
        datepicker=convert(date_format),
        datetimepicker=convert(datetime_format),
        language=request.LANGUAGE_CODE,
    )
