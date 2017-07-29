# coding: utf-8

from django.forms import ModelForm


class BaseForm(ModelForm):
    required_css_class = 'form-group'
