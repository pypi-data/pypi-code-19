from django.conf import settings

from .transports.threaded import ThreadedHTTPTransport
from . import memoize


class ZipKinTransport(object):
    """
    HTTP Transporter class
    """

    _uri = '/api/v1/spans'

    def __init__(self):
        self.use_ssl = False
        self.url = "http://%s:%s%s" % (
            settings.ZIPKIN_SERVER_HOST,
            settings.ZIPKIN_SERVER_PORT, self._uri)

        self.timeout = settings.ZIPKIN_REQUEST_TIMEOUT
        self.async = (settings.ZIPKIN_TRANSPORT_ASYNC and True)
        self._tracing_enabled = settings.ZIPKIN_TRACING_ENABLED
        self.headers = {'Content-Type': 'application/x-thrift'}

    @memoize
    def transport(self):
        return ThreadedHTTPTransport(
            self.url, verify_ssl=self.use_ssl,
            timeout=self.timeout)

    @property
    def is_tracing_enabled(self):
        return self._tracing_enabled

    @property
    def method(self):
        method = (
            'async_send' if self.async else 'send_sync'
        )
        return method

    def format(self, encoded_span):
        body = '\x0c\x00\x00\x00\x01' + encoded_span
        return body

    def __call__(self, encoded_span):
        if not self.is_tracing_enabled:
            return

        span = self.format(encoded_span)
        return self._emit(span)

    def _emit(self, span):
        print span
        fn = getattr(self.transport, self.method)
        return fn(data=span, headers=self.headers)


transport_handler = ZipKinTransport()
