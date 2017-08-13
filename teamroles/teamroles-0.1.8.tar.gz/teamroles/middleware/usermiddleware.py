from threading import local

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError as ie:
    MiddlewareMixin = object

_tls = local()


class CurrentUserMiddleware(MiddlewareMixin):
    """
    Middleware that handles temporary messages.
    """

    def process_request(self, request):
        """
        Set up TLS' user and request
        """
        _tls.request = request
        _tls.user = getattr(request, 'user', None)

    def process_response(self, request, response):
        """
        Clean TLS after response
        """
        _tls.request = None
        _tls.user = None
        return response

    def process_exception(self, request, exception):
        """
        Clean TLS after exception
        """
        _tls.request = None
        _tls.user = None
