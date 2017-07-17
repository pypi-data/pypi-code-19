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
    time_format = get_format('TIME_INPUT_FORMATS')[0]
    request = context['request']
    datepicker_i18n = 'ms_utils/js/datepicker-i18n/bootstrap-datepicker.{}.min.js'.format(request.LANGUAGE_CODE)

    return dict(
        daterangepicker=convert(date_format),
        datepicker=convert(date_format).lower(),
        timepicker=convert(time_format),
        language=request.LANGUAGE_CODE,
        datepicker_i18n=datepicker_i18n,
    )
