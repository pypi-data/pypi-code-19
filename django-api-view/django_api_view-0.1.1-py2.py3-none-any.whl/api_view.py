# -*- coding: utf-8
# pylint: disable=W0612,W0703

# Django
import json
from django.views.generic import View
from django.http import QueryDict
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class ApiView(View):

    @staticmethod
    def _parse_content_type(content_type):
        if ';' in content_type:
            content_type, params = content_type.split(';', 1)
            try:
                params = dict(param.split('=') for param in params.split())
            except Exception:
                params = {}
        else:
            content_type = content_type
            params = {}

        return content_type, params

    def _parse_body(self, request):
        # If method not in post, put, or patch return
        if request.method not in ['POST', 'PUT', 'PATCH']:
            return

        content_type, params = self._parse_content_type(request.content_type)
        charset = params.get('charset', 'utf-8')

        if content_type == 'application/json':
            try:
                data = request.body.decode(charset)
                request.data = json.loads(data)
            except Exception:
                raise
        elif (content_type == 'application/x-www-form-urlencoded' or
              content_type.startswith('multipart/form-data')):
            request.data = QueryDict(request.body, encoding=charset)
        else:
            request.data = request.body

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        request.content_type = request.META.get('CONTENT_TYPE', 'text/plain')
        request.params = dict((k, v) for (k, v) in request.GET.items())
        request.data = None
        request.raw_data = request.body

        try:
            self._parse_body(request)
            response = super(ApiView, self).dispatch(request, *args, **kwargs)
        except Exception:
            raise

        return response
