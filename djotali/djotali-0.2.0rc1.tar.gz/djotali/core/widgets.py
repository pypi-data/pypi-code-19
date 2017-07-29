# coding: utf-8
import inspect
import os
from ast import literal_eval
from datetime import timedelta

from django import forms
from django.conf import settings
from django.forms import Widget
from django.forms.renderers import BaseRenderer
from django.template.backends.django import DjangoTemplates
from django.utils.datetime_safe import datetime
from django.utils.functional import cached_property


class CoreEngineMixin(object):
    def get_template(self, template_name):
        return self.engine.get_template(template_name)

    @cached_property
    def engine(self):
        return self.backend({
            'APP_DIRS': True,
            'DIRS': [os.path.join(settings.BASE_DIR, 'djotali', 'templates'),
                     os.path.join(os.path.dirname(inspect.getfile(BaseRenderer)), 'templates')],
            'NAME': 'corewidgets',
            'OPTIONS': {},
        })


# Copied from django.forms.renderers.DjangoTemplates
class CoreTemplatesRenderer(CoreEngineMixin, BaseRenderer):
    """
    Load Django templates from the built-in widget templates in
    django/forms/templates and from apps' 'templates' directory.
    """
    backend = DjangoTemplates


class CoreWidget(Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return super().render(name, value, attrs, CoreTemplatesRenderer())


DATE_FORMAT = '%d/%m/%Y'
TIME_FORMAT = '%H:%M'


class DateTimeFieldWidget(forms.DateTimeInput, CoreWidget):
    template_name = 'core/widgets/datetime.html'

    def __init__(self, attrs=None):
        final_attrs = {'class': 'mydatepicker'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(DateTimeFieldWidget, self).__init__(attrs=final_attrs)

    def get_context(self, name, value, attrs):
        context = super(DateTimeFieldWidget, self).get_context(name, value, attrs)
        # The expected format is explained in the available options -> data-default-date here http://felicegattuso.com/projects/datedropper/
        context['widget']['date'] = (value if value is not None else DateTimeFieldWidget._get_date_in_one_week()).strftime('%m/%d/%Y')
        context['widget']['time'] = value.strftime('%H:%M') if value is not None else '09:00'
        return context

    @staticmethod
    def _get_date_in_one_week():
        now = datetime.now()
        one_week = timedelta(weeks=1)
        return now + one_week

    def value_from_datadict(self, data, files, name):
        try:
            return datetime.strptime('{} {}'.format(data.get('start_date_day'), data.get('start_date_time')),
                                     '{} {}'.format(DATE_FORMAT, TIME_FORMAT))
        except ValueError:
            # The provided value does not match the expected format so we ignore it
            return None

    class Media:
        css = {
            'all': ('css/datedropper.min.css', 'css/jquery-clockpicker.min.css')
        }
        js = ('js/moment.min.js', 'js/bootstrap-datepicker.min.js', 'js/datedropper.min.js', 'js/jquery-clockpicker.min.js', 'js/pickers.js')


class BoundModelsTableWidget(forms.widgets.Input, CoreWidget):
    template_name = 'core/widgets/bound_models_table.html'

    def value_from_datadict(self, data, files, name):
        return self._get_value(data, name)

    def value_omitted_from_data(self, data, files, name):
        models_dict = self._get_value(data, name)
        return not isinstance(models_dict, list)

    def _get_value(self, data, name):
        return literal_eval(data['id_{}_container_input'.format(name)])

    class Media:
        js = (
            settings.AXIOS_LIB,
            settings.VUE_LIB,
            settings.VUEX_LIB,
            'js/typeahead.bundle.min.js',
            'js/vue-bootstrap4-typeahead.component.js',
            'js/linked-models/linked-models-addition.component.js',
            'js/linked-models/linked-models.store.js',
            'js/linked-models/linked-models-paginator.component.js',
            'js/linked-models/linked-models-table.component.js',
            'js/linked-models/linked-models-components.js',
        )

        css = {
            'all': ('css/typehead-min.css',)
        }


class BoundModelsSelectWidget(forms.widgets.Select, CoreWidget):
    template_name = 'core/widgets/bound_models_select.html'

    def get_context(self, name, value, attrs):
        context = super(BoundModelsSelectWidget, self).get_context(name, value, attrs)
        if value is not None:
            widget_url = self.get_url(value)
            if widget_url is not None:
                context["widget"]["edit_url"] = widget_url
        context["widget"]["edit_label"] = self.get_label()
        return context

    def get_url(self, value):
        raise NotImplementedError

    def get_label(self):
        raise NotImplementedError
