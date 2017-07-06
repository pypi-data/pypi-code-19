# TODO: to be removed, for testing ui
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

def home(request):
    return render(request, 'intlekt/home.html')

def usl_tagger(request):
    return render(request, 'intlekt/uslTagger.html')

@require_http_methods(["POST"])
@csrf_exempt
def scoopit(request):
    print(request.body)

    return HttpResponse('scoopit')


from . import collections
from . import library
