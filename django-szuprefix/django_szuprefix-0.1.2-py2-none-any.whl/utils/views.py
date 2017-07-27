# -*- coding:utf-8 -*-
from django.core.urlresolvers import reverse
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.views.generic import View

from django_szuprefix.utils.formutils import form2dict


class FormResponseJsonMixin(object):
    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse(
            dict(code=0, msg='ok', data=model_to_dict(self.object, fields=self.get_form_class().Meta.fields)))

    def form_invalid(self, form):
        return JsonResponse(dict(code=1, msg=u'表单检验不通过', data=dict(errors=form.errors)))

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            return JsonResponse(dict(code=0, msg='ok', data=form2dict(context['form'])))
        return super(FormResponseJsonMixin, self).render_to_response(context, **response_kwargs)

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
