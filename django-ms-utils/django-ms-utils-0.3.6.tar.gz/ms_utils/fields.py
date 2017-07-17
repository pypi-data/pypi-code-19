from django.conf import settings
from django import forms
from . import widgets

class DateTimePickerField(forms.SplitDateTimeField):
    widget = widgets.DateTimePickerWidget()

class DatePickerField(forms.DateField):
    widget = widgets.DatePickerWidget()

class TimePickerField(forms.TimeField):
    widget = widgets.TimePickerWidget()
