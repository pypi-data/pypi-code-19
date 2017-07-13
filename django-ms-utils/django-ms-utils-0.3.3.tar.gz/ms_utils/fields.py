from django.conf import settings
from django import forms
from django.forms import widgets


class DatePickerField(forms.DateField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = widgets.DateInput(attrs={'data-role':'datepicker'})
        super().__init__(*args, **kwargs)

class DateTimePickerField(forms.DateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = widgets.DateInput(attrs={'data-role':'datetimepicker'})
        super().__init__(*args, **kwargs)
