from __future__ import unicode_literals

from django import template
from django.conf import settings

register = template.Library()

STATIC_PREFIX = '%sclick_captcha/' % settings.STATIC_URL


@register.inclusion_tag('click_captcha/js.html')
def include_click_captcha_js(jquery=True):
    return {'prefix': STATIC_PREFIX, 'jquery': jquery}


@register.inclusion_tag('click_captcha/css.html')
def include_click_captcha_css(bootstrap=True):
    return {'prefix': STATIC_PREFIX, 'bootstrap': bootstrap}
