import requests

import simplejson
from django.conf import settings

AC_HEADERS = {
    'X-Angie-AuthApiToken': settings.AC_TOKEN,
    'Content-Type': 'application/json; charset=utf-8'
}


def get_activecollab(api_path, params=None):
    r = requests.get('{}{}'.format(
        settings.AC_API_URL, api_path), params=simplejson.dumps(params),
        headers=AC_HEADERS)

    return r


def post_activecollab(api_path, params=None):
    r = requests.post('{}{}'.format(
        settings.AC_API_URL, api_path), data=simplejson.dumps(params),
        headers=AC_HEADERS)

    return r
