__version__ = '0.1.1'

from django.forms.widgets import HiddenInput


class InitialFieldsMixin(object):
    def clean(self):
        cleaned_data = super(InitialFieldsMixin, self).clean()
        for hidden_field in self.initial_fields:
            cleaned_data[hidden_field] = self.initial[hidden_field]
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(InitialFieldsMixin, self).__init__(*args, **kwargs)
        for hidden_field in self.initial_fields:
            self.fields[hidden_field].widget = HiddenInput()
            self.fields[hidden_field].required = False
