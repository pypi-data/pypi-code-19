__version__ = '0.1.0'

from django.forms.widgets import HiddenInput


class InitialFieldsMixin(object):
    def clean(self):
        for hidden_field in self.initial_fields:
            self.cleaned_data[hidden_field] = self.initial[hidden_field]
        super(InitialFieldsMixin, self).clean()

    def __init__(self, *args, **kwargs):
        super(InitialFieldsMixin, self).__init__(*args, **kwargs)
        for hidden_field in self.initial_fields:
            self.fields[hidden_field].widget = HiddenInput()
            self.fields[hidden_field].required = False
