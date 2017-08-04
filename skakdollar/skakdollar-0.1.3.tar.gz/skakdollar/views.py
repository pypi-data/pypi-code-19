# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from .translate import DefaultTranslator


# Create your views here.

class IndexPageView(TemplateView):
    template_name = 'skakdollar/index.html'


@csrf_exempt
def translate(request):
    original = json.loads(request.body)
    translator = DefaultTranslator()
    response = dict(response=list(translator.translate(original['msg'])))
    return HttpResponse(json.dumps(response), content_type='application/json')
