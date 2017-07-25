# coding: utf-8
from django.forms.widgets import NullBooleanSelect


class CaseLessNullBooleanSelect(NullBooleanSelect):
    """
    NullBooleanSelect, дополненный возможностью указывать в запросе true и
    false, вместо True и False
    """
    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        return {
            '2': True,
            True: True,
            'True': True,
            'true': True,
            '3': False,
            'False': False,
            'false': False,
            False: False,
        }.get(value)