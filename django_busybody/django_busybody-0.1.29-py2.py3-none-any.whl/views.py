# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import io

from six.moves.urllib.parse import quote

from django.http.response import HttpResponse
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormMixin, ProcessFormView
from django.core.exceptions import ImproperlyConfigured
from django.forms import models as model_forms
from django.views.generic.base import ContextMixin

from .datas import CsvDataMixin, ZipDataMixin


class SearchFormMixin(FormMixin):
    def get_form(self, *args, **kwargs):
        form = super(SearchFormMixin, self).get_form()
        form.bound_css_class = ''
        for i in form.fields:
            field = form.fields[i]
            field.required = False
        return form

    def get_form_kwargs(self):
        kwargs = super(SearchFormMixin, self).get_form_kwargs()
        d = dict(self.request.GET.items())
        for key, value in self.get_initial().items():
            if key not in d:
                d[key] = value
        kwargs.update({
            'data': d
        })
        return kwargs


class MultipleObjectMixin(ContextMixin):
    model_map = {}
    pk_url_kwarg = '{}_pk'

    def get_objects(self):
        return {
            key: model._default_manager.all().get(
                pk=self.kwargs.get(self.pk_url_kwarg.format(key)))
            for key, model in self.model_map.items()
        }


class MultipleFormMixin(FormMixin):
    initial_map = {}
    form_class_map = {}
    prefix_map = {}

    def get_initial(self, key):
        return self.initial_map.get(key, {})

    def get_prefix(self, key):
        return self.prefix_map.get(key, key)

    def get_form_class(self, key):
        return self.form_class_map[key]

    def get_form(self, key, form_class=None):
        """
        Returns an instance of the form to be used in this view.
        """
        if form_class is None:
            form_class = self.get_form_class(key)
        return form_class(**self.get_form_kwargs(key))

    def get_form_kwargs(self, key):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {
            'initial': self.get_initial(key),
            'prefix': self.get_prefix(key),
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_form_class_keys(self):
        return self.form_class_map.keys()

    def get_forms(self):
        return {
            key: self.get_form(key)
            for key in self.get_form_class_keys()
        }

    def get_context_data(self, **kwargs):
        """
        Insert the form into the context dict.
        """
        for key in self.get_form_class_keys():
            kwargs['{}_form'.format(key)] = self.get_form(key)
        return super(FormMixin, self).get_context_data(**kwargs)


class MultipleModelFormMixin(MultipleFormMixin, MultipleObjectMixin):
    fields = {}

    def get_form_class(self, key):
        if self.fields.get(key) is not None and self.form_class_map.get(key):
            raise ImproperlyConfigured(
                "Specifying both 'fields' and 'form_class' is not permitted."
            )
        if self.form_class_map.get(key):
            return self.form_class_map.get(key)
        else:
            if self.model_map.get(key) is not None:
                # If a model has been explicitly provided, use it
                model = self.model_map.get(key)
            elif (hasattr(self, '{}_object'.format(key)) and
                  getattr(self, '{}_object'.format(key)) is not None):
                # If this view is operating on a single object, use
                # the class of that object
                model = self.object.__class__
            else:
                # Try to get a queryset and extract the model class
                # from that
                model = self.get_queryset().model

            if self.fields is None:
                raise ImproperlyConfigured(
                    "Using ModelFormMixin (base class of %s) without "
                    "the 'fields' attribute is prohibited." % self.__class__.__name__
                )

            return model_forms.modelform_factory(model, fields=self.fields.get(key))

    def get_form_kwargs(self, key):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(MultipleModelFormMixin, self).get_form_kwargs(key)
        if hasattr(self, '{}_object'.format(key)):
            kwargs.update({'instance': getattr(self, '{}_object'.format(key))})
        return kwargs

    def get_form_class_keys(self):
        s = set(self.form_class_map.keys())
        s.update(self.model_map.keys())
        return list(s)

    def form_valid(self, forms):
        """
        If the form is valid, save the associated model.
        """
        for key, form in forms.items():
            setattr(self, '{}_object'.format(key), form.save())
        return super(MultipleModelFormMixin, self).form_valid(forms)


class ProcessMultipleFormView(ProcessFormView):
    def post(self, request, *args, **kwargs):
        forms = self.get_forms()
        if min(x.is_valid() for x in forms.values()):
            return self.form_valid(forms)
        else:
            return self.form_invalid(forms)


class BaseMultipleFormView(MultipleFormMixin, ProcessMultipleFormView):
    pass


class MultipleFormView(TemplateResponseMixin, BaseMultipleFormView):
    pass


class MultipleUpdateView(MultipleModelFormMixin, TemplateResponseMixin, ProcessMultipleFormView):
    def dispatch(self, *args, **kwargs):
        for key, obj in self.get_objects().items():
            setattr(self, '{}_object'.format(key), obj)
        return super(MultipleUpdateView, self).dispatch(*args, **kwargs)


class DownloadMixin(object):
    download_filename = 'download'
    data_content_type = 'application/octet-stream'

    def get_data_content_type(self):
        return self.data_content_type

    def get_filename(self):
        return self.download_filename

    def download(self, **kwargs):
        buf = io.BytesIO()
        self.write_data(buf, **kwargs)
        buf.seek(0)
        response = HttpResponse(
            buf, content_type=self.get_data_content_type())
        response['Content-Disposition'] = (
            "attachment; filename*=utf-8'jp'{}".format(
                quote(self.get_filename().encode('UTF-8'))))
        return response


class DownloadCsvMixin(CsvDataMixin, DownloadMixin):
    def get_data_content_type(self):
        return 'text/csv; charset={}'.format(self.get_encoding())


class DownloadZipMixin(ZipDataMixin, DownloadMixin):
    pass
