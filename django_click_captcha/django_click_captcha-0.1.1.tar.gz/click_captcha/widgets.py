import uuid

import django
from django.forms.widgets import Widget
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from click_captcha.client_settings import WIDGET_TEMPLATE, TIMEOUT


# from django.core.urlresolvers import reverse

class Captcha(Widget):
    template_name = WIDGET_TEMPLATE
    timeout = TIMEOUT
    click_captcha_id = 'click_captcha_id'
    click_captcha_value = 'click_captcha_value'

    def render(self, name, value, attrs=None, renderer=None):
        if django.VERSION < (1, 11):
            return mark_safe(render_to_string(
                self.template_name,
                self.get_context(name, value, attrs)
            ))
        else:
            return super(Captcha, self).render(
                name, value, attrs=attrs, renderer=renderer
            )

    def value_from_datadict(self, data, files, name):
        return [
            data.get(self.click_captcha_id, None),
            data.get(self.click_captcha_value, None)
        ]

    def captcha_cache_key_gen(self):
        return str(uuid.uuid1()).replace('-', '')

    def get_context(self, name, value, attrs):
        try:
            context = super(Captcha, self).get_context(name, value, attrs)
        except AttributeError:
            context = {
                "widget": {
                    "attrs": self.build_attrs(attrs)
                }
            }

        context.update({
            'timeout': self.timeout,
            'uuid': self.captcha_cache_key_gen(),
            'id_name': self.click_captcha_id,
            'value_name': self.click_captcha_value
        })
        return context
