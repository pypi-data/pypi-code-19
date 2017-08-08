import logging
import traceback

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core.models import http
from aws_xray_sdk.core.models.trace_header import TraceHeader


log = logging.getLogger(__name__)

# Django will rewrite some http request headers.
USER_AGENT_KEY = 'HTTP_USER_AGENT'
X_FORWARDED_KEY = 'HTTP_X_FORWARDED_FOR'
REMOTE_ADDR_KEY = 'REMOTE_ADDR'
XRAY_HEADER_KEY = 'HTTP_X_AMZN_TRACE_ID'
HOST_KEY = 'HTTP_HOST'
CONTENT_LENGTH_KEY = 'content-length'


class XRayMiddleware(object):
    """
    Middleware that wraps each incoming request to a segment.
    """
    def __init__(self, get_response):

        self.get_response = get_response

    # hooks for django version >= 1.10
    def __call__(self, request):
        # a segment name is required
        name = xray_recorder.service
        xray_header = self._get_tracing_header(request)
        if not xray_header:
            xray_header = TraceHeader()

        sampling_decision = None
        meta = request.META
        # sampling decision from incoming request's header has highest precedence
        if xray_header.sampled is not None:
            sampling_decision = xray_header.sampled
        elif not xray_recorder.sampling:
            sampling_decision = 1
        elif xray_recorder.sampler.should_trace(
            service_name=meta.get(HOST_KEY),
            method=request.method,
            path=request.path,
        ):
            sampling_decision = 1
        else:
            sampling_decision = 0

        segment = xray_recorder.begin_segment(
            name=name,
            traceid=xray_header.root,
            parent_id=xray_header.parent,
            sampling=sampling_decision,
        )

        segment.put_http_meta(http.URL, request.build_absolute_uri())
        segment.put_http_meta(http.METHOD, request.method)

        if meta.get(USER_AGENT_KEY):
            segment.put_http_meta(http.USER_AGENT, meta.get(USER_AGENT_KEY))
        if meta.get(X_FORWARDED_KEY):
            # X_FORWARDED_FOR may come from untrusted source so we
            # need to set the flag to true as additional information
            segment.put_http_meta(http.CLIENT_IP, meta.get(X_FORWARDED_KEY))
            segment.put_http_meta(http.X_FORWARDED_FOR, True)
        elif meta.get(REMOTE_ADDR_KEY):
            segment.put_http_meta(http.CLIENT_IP, meta.get(REMOTE_ADDR_KEY))

        response = self.get_response(request)

        status_code = int(response.status_code)
        segment.apply_status_code(status_code)
        segment.put_http_meta(http.STATUS, status_code)

        if response.has_header(CONTENT_LENGTH_KEY):
            length = int(response[CONTENT_LENGTH_KEY])
            segment.put_http_meta(http.CONTENT_LENGTH, length)

        xray_recorder.end_segment()

        return response

    def process_exception(self, request, exception):
        """
        Add exception information and fault flag to the
        current segment.
        """
        segment = xray_recorder.current_segment()
        segment.add_fault_flag()

        stack = traceback.extract_stack(limit=xray_recorder._max_trace_back)
        segment.add_exception(exception, stack)

    def _get_tracing_header(self, request):

        header = request.META.get(http.XRAY_HEADER)

        if not header:
            header = request.META.get(XRAY_HEADER_KEY)
        if not header:
            return None

        return TraceHeader.from_header_str(header)
