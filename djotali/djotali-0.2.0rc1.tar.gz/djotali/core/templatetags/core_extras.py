# coding: utf-8
from django import template

register = template.Library()


@register.filter()
def as_percent(value, total):
    return round(100 * float(value) / total, 1)


@register.simple_tag
def relative_url(value, field_name, urlencode=None):
    url = '?{}={}'.format(field_name, value)
    if urlencode:
        querystring = urlencode.split('&')
        filtered_querystring = filter(lambda p: p.split('=')[0] != field_name, querystring)
        encoded_querystring = '&'.join(filtered_querystring)
        url = '{}&{}'.format(url, encoded_querystring)
        if url.endswith('&'):
            url = url[:-1]
    return url


@register.filter(name='add_class')
def add_class(field, class_attr):
    if field.errors:
        class_attr += ' form-control-danger'
    return field.as_widget(attrs={'class': field.css_classes(class_attr)})
