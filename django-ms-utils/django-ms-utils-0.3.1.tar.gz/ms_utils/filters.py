from django import forms
from django.forms import widgets
from django.utils.translation import gettext_lazy as _
from django_filters import ModelChoiceFilter, ModelMultipleChoiceFilter, \
    DateFromToRangeFilter, BooleanFilter
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget


boolean_choices = (
    ('', _('All')),
    ('0', _('No')),
    ('1', _('Yes')),
)

def model_filter(model, search_fields, multiple=False, queryset=None, attrs=None):
    if not queryset:
        queryset = model.objects.all()

    if not isinstance(search_fields, (list, tuple)):
        search_fields = [search_fields]

    if multiple:
        filter_cls = ModelMultipleChoiceFilter
        widget_cls = ModelSelect2MultipleWidget
    else:
        filter_cls = ModelChoiceFilter
        widget_cls = ModelSelect2Widget

    return filter_cls(
        queryset=queryset,
        widget=widget_cls(
            model=model,
            search_fields=search_fields,
            attrs=attrs,
        ),
    )

class DateRangeWidget(widgets.TextInput):
    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs['data-role'] = 'daterangepicker'
        return attrs

    def format_value(self, value):
        if not value:
            return ''
        return ' - '.join(value)

    def value_from_datadict(self, data, files, name):
        return data.get(name, '').split(' - ')

class DateRangePickerFilter(DateFromToRangeFilter):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = DateRangeWidget()
        super().__init__(*args, **kwargs)

class BooleanChoiceFilter(BooleanFilter):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = forms.RadioSelect(choices=boolean_choices)
        super().__init__(*args, **kwargs)
