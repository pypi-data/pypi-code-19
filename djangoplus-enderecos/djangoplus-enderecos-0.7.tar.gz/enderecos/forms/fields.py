# -*- coding: utf-8 -*-
from django import forms
from enderecos.forms import widgets


class CepField(forms.fields.RegexField):
    widget = widgets.CepWidget

    default_error_messages = {
        'invalid': u'O CEP deve estar no formato XX.XXX-XXX.',
    }

    def __init__(self, *args, **kwargs):
        super(CepField, self).__init__(r'^\d{2}\.\d{3}-\d{3}$', *args, **kwargs)
