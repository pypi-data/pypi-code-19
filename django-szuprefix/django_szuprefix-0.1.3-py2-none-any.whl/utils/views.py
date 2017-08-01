# -*- coding:utf-8 -*-
from django.core.urlresolvers import reverse
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.views.generic import View

from .modelutils import object2dict4display
from .formutils import form2dict
from .tableutils import table2dict


class ContextJsonDumpsMixin(object):
    json_contexts = {}

    def get_json_contexts(self, context):
        res = {}
        res.update(self.json_contexts)
        return res

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax() or self.request.GET.get("format_") == 'json':
            return JsonResponse(dict(code=0, msg='ok', data=self.get_json_contexts(context)))
        return super(ContextJsonDumpsMixin, self).render_to_response(context, **response_kwargs)


class FormResponseJsonMixin(object):
    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse(
            dict(code=0, msg='ok'))

    def form_invalid(self, form):
        return JsonResponse(dict(code=1, msg=u'表单检验不通过', data=dict(errors=form.errors)))

    def get_json_contexts(self, context):
        ctx = super(FormResponseJsonMixin, self).get_json_contexts(context)
        ctx['form'] = form2dict(context['form'])
        if hasattr(self, 'object') and self.object:
            ctx['object'] = model_to_dict(self.object, fields=self.get_form_class().Meta.fields)
        return ctx


class TableResponseJsonMixin(object):
    def get_json_contexts(self, context):
        ctx = super(TableResponseJsonMixin, self).get_json_contexts(context)
        ctx['table'] = table2dict(context['table'])
        return ctx


class ObjectResponseJsonMixin(object):
    fields_display = ['id']

    def get_fields_display(self):
        return self.fields_display

    def get_json_contexts(self, context):
        ctx = super(ObjectResponseJsonMixin, self).get_json_contexts(context)
        ctx['object'] = object2dict4display(context['object'], self.get_fields_display())
        return ctx


def csrf_token(request):
    from django.middleware.csrf import get_token
    get_token(request)
    return JsonResponse(dict(code=0, msg="ok"))


class LoginRequiredJsView(View):
    def get(self, request, *args, **kwargs):
        from django.middleware.csrf import get_token
        get_token(request)
        if request.user.is_authenticated():
            return HttpResponse("")
        else:
            return HttpResponse("window.location.href = '%s'" % reverse("accounts:login"))
