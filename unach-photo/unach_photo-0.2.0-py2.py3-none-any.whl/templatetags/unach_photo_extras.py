from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
import requests

from unach_photo.models import Picture

register = template.Library()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest'
}


@register.filter
@stringfilter
def get_photo(photo_name):

    pictures = Picture.objects.filter(
        identificador__iexact=photo_name
    )

    if pictures.exists():
        return pictures[0].url
    else:
        url = '{0}{1}'.format(
            settings.VALID_HOST,
            '/pictures/photo/'
        )

        params = {
            'photo_name': photo_name,
            'token': settings.VALID_TOKEN,
            'refresh': True
        }

        r = requests.get(
            url,
            params=params,
            headers=HEADERS
        )

        json_response = r.json()

        if json_response['success']:
            '''
                Respuesta satisfactoria
            '''
            if json_response['type'] == 'blob':
                '''
                    viene de database
                '''
            else:
                '''
                    viene de sistema de archivos
                '''
                url = json_response['url']
                Picture.objects.create(
                    identificador=photo_name,
                    url=url
                )
                return url
        r.close()

    return None


@register.filter
@stringfilter
def get_photo_blob(photo_name):

    url = '{0}{1}'.format(
        settings.VALID_HOST,
        '/pictures/photo/blob/'
    )

    params = {
        'photo_name': photo_name,
        'token': settings.VALID_TOKEN
    }

    r = requests.get(
        url,
        params=params,
        headers=HEADERS
    )

    json_response = r.json()

    if json_response:

        if json_response['success']:
            '''
                Respuesta satisfactoria
            '''
            return "data:image/png;base64,{0}".format(
                json_response['url']
            )

    r.close()

    return None
