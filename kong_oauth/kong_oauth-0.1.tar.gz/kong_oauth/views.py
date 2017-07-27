# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import AuthenticationForm

import requests, json

def index(request):
    data = {}
    for key, value in request.META.items():
        if key.startswith('HTTP_X_'):
            data[key] = value
    data['user_id'] = request.user.id
    data['is_authenticated'] = request.user.is_authenticated()
    return JsonResponse(data)

@require_http_methods(["GET", "POST"])
@csrf_exempt
def token(request):

    next = request.GET.get('next')

    if request.method == 'GET':
        form = AuthenticationForm()
        context = {
            "form": form
        }
        return render(request, 'kong_oauth/login.html', context = context)

    is_form_data = 'json' not in request.META.get('CONTENT_TYPE').lower()

    if is_form_data:
        username = request.POST['username']
        password = request.POST['password']
        client_id = request.POST.get('client_id')
        client_secret = request.POST.get('client_secret')
    else:
        payload = json.loads(request.body)
        username = payload['username']
        password = payload['password']
        client_id = payload.get('client_id'), # 1
        client_secret = payload.get('client_secret')

    base_url = getattr(settings, 'KONG_GATEWAY_URL')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        data = {
            "client_id": client_id,
            "client_secret": client_secret, # testtest
            "grant_type": "password",
            "provision_key": settings.KONG_PROVISION_KEY,
            "authenticated_userid": user.id,
            "username": username,
            "password": password
        }
        url = "{}/oauth2/token".format(base_url)
        url = 'https://invoiceguru.appointmentguru.co/oauth2/token/'
        print(url)
        print(data)
        result = requests.post(url, data, verify=False)
        status = result.status_code
        result = result.json()
    else:
        result = {
            'message': 'Authentication failed. Invalid username or password'
        }
        status = 401

    return JsonResponse(result, status=status)
