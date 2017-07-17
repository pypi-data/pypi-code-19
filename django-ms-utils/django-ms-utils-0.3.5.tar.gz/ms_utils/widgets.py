from django.forms import widgets


class MultiSelectWidget(widgets.SelectMultiple):
    template_name = 'ms_utils/widgets/multiselect.html'

    def __init__(self, *args, **kwargs):
        self.size = 'medium'
        if 'size' in kwargs:
            self.size = kwargs['size']
            del kwargs['size']
        attrs = kwargs.setdefault('attrs', dict())
        attrs['data-role'] = 'multiselect'
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['size'] = self.size
        return context

class DateTimePickerWidget(widgets.SplitDateTimeWidget):
    template_name = 'ms_utils/widgets/datetimepicker.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widgets[0].attrs['data-role'] = 'datepicker'
        self.widgets[1].attrs['data-role'] = 'timepicker'

class DatePickerWidget(widgets.DateInput):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.setdefault('attrs', dict())
        attrs['data-role'] = 'datepicker'
        super().__init__(*args, **kwargs)

class TimePickerWidget(widgets.TimeInput):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.setdefault('attrs', dict())
        attrs['data-role'] = 'timepicker'
        super().__init__(*args, **kwargs)
