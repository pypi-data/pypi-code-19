from django import forms
from click_captcha.fields import CaptchaField


class CaptchaForm(forms.Form):
    captcha = CaptchaField()
