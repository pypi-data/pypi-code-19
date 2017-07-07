from __future__ import absolute_import, unicode_literals

from django.template import Library

from wagtail.wagtailcore.models import Site

from ..context_processors import SettingsProxy

register = Library()


@register.simple_tag(takes_context=True)
def get_settings(context, use_default_site=False):
    if use_default_site:
        site = Site.objects.get(is_default_site=True)
    elif 'request' in context:
        site = context['request'].site
    else:
        raise RuntimeError('No request found in context, and use_default_site '
                           'flag not set')

    context['settings'] = SettingsProxy(site)
    return ''
