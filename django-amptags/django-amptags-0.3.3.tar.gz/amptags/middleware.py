import re
from urllib.parse import urlsplit

from django.conf import settings
from django.http import HttpRequest, HttpResponseBadRequest


def amp_post_middleware(get_response):
    """
    Factory for middleware that processes or rejects POST requests based on Google AMP guidelines:
    https://github.com/ampproject/amphtml/blob/master/spec/amp-cors-requests.md
    """

    def middleware(request: HttpRequest):
        pass


class AMPPostMiddleware(object):
    """
    Processes and possibly rejects incoming POST requests based on Google AMP guidelines:
    https://github.com/ampproject/amphtml/blob/master/spec/amp-cors-requests.md
    """

    AMP_HOSTS = [
        re.compile(r'^.+\.ampproject\.org$'),
        re.compile(r'^.+\.amp\.cloudflare\.com$'),
    ]

    SEE_ALSO = 'See https://github.com/ampproject/amphtml/blob/master/spec/amp-cors-requests.md'

    def __init__(self, get_response: callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):

        # AMP rules only apply to POST requests
        if request.method != 'POST':
            return self.get_response(request)

        # AMP rules only apply to requests sent by the AMP runtime
        amp_source_origin = request.GET.get('__amp_source_origin')
        if not amp_source_origin:
            return self.get_response(request)

        origin = request.META.get('HTTP_ORIGIN')

        # If the origin header is present...
        if origin:

            # Confirm origin matches our own hosts or official AMP hosts
            parts = urlsplit(origin)
            if parts.hostname not in settings.ALLOWED_HOSTS:
                found = False
                for pattern in AMPPostMiddleware.AMP_HOSTS:
                    if pattern.match(parts.hostname):
                        found = True
                        break
                if not found:
                    message = 'The request origin does not match one of the allowed hosts. ' + AMPPostMiddleware.SEE_ALSO
                    return HttpResponseBadRequest(message)

            # Confirm __amp_source_origin query parameter is our host
            parts = urlsplit(amp_source_origin)
            if parts.hostname not in settings.ALLOWED_HOSTS:
                message = 'The __amp_source_origin does not match one of the allowed hosts. ' + AMPPostMiddleware.SEE_ALSO
                return HttpResponseBadRequest(message)

        # Otherwise if the origin header is not present...
        else:

            amp_same_origin = request.META.get('AMP_SAME_ORIGIN', '')
            if amp_same_origin.lower() != 'true':
                message = 'The AMP-Same-Origin header must be present if the Origin header is not. ' + AMPPostMiddleware.SEE_ALSO
                return HttpResponseBadRequest(message)
            origin = amp_source_origin = request.get_host()

        # Process the request
        response = self.get_response(request)

        # Set required outgoing headers
        response['Access-Control-Allow-Origin'] = origin
        response['AMP-Access-Control-Allow-Source-Origin'] = amp_source_origin
        response['Access-Control-Expose-Headers'] = 'AMP-Access-Control-Allow-Source-Origin'

        return response





