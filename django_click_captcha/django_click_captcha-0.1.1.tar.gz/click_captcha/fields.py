from django import forms
from django.core.cache import cache
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _
from inspect import isfunction
from click_captcha import widgets


class CaptchaField(forms.Field):
    widget = widgets.Captcha

    default_error_messages = {
        'captcha_invalid': _('Incorrect, please try again.'),
        'captcha_error': _('Error verifying input, please try again.'),
        'captcha_timeout': _('captcha has expired, please refresh and try again')
    }

    def __init__(self, **kwargs):

        _id = kwargs.pop('click_captcha_id', None)
        _value = kwargs.pop('click_captcha_value', None)
        _func = kwargs.pop('captcha_cache_key_gen_func', None)
        super(CaptchaField, self).__init__(**kwargs)
        if _id:
            self.widget.click_captcha_id = _id
        if _value:
            self.widget.click_captcha_value = _value
        if _func:
            self.widget.captcha_cache_key_gen = _func

    def clean(self, value):

        if not isinstance(value, list) or len(value) != 2 or not bool(value[0]) or not bool(value[1]):
            raise ValidationError(
                self.error_messages['captcha_error']
            )
        try:
            captcha_value = [float(item) for item in value[1].split(',')]

            if len(captcha_value) % 2 != 0:
                raise ValidationError(
                    self.error_messages['captcha_error']
                )
        except ValueError:
            raise ValidationError(
                self.error_messages['captcha_error']
            )

        captcha, width, height = cache.get(value[0], (None, None, None))

        if captcha is None:
            raise ValidationError(
                self.error_messages['captcha_timeout']
            )
        # 数目不一致
        if len(captcha) * 2 != len(captcha_value):
            raise ValidationError(
                self.error_messages['captcha_invalid']
            )

        for index, value in enumerate(captcha_value):
            if index % 2 == 0:  # width
                temp_index = int(index / 2)
                if captcha[temp_index] <= value < captcha[temp_index] + width:
                    pass
                else:
                    raise ValidationError(
                        self.error_messages['captcha_invalid']
                    )
            else:
                if 0 <= value < height:
                    pass
                else:
                    raise ValidationError(
                        self.error_messages['captcha_invalid']
                    )
        return captcha