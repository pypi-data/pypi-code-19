import time
import uuid

from django_xray import traces, records, xray


class XRayMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        trace = self._create_new_segment(request)
        xray.set_current_trace(trace)

        try:
            response = self.get_response(request)
            trace.http.response_status_code = response.status_code
            return response
        finally:
            trace.end_time = time.time()
            xray.connection.send(trace)
            xray.set_current_trace(None)

    def _create_new_segment(self, request):
        trace_id = request.META.get('X-Amzn-Trace-Id')
        http_data = None
        if not trace_id:
            trace_id = '1-%08x-%s' % (int(time.time()), uuid.uuid4().hex[:24])

        http_data = records.HttpRecord(
            request_method=request.method,
            request_url=request.get_full_path(),
            request_user_agent=request.META.get('User-Agent'))

        segment = records.SegmentRecord(
            name='django.request',
            start_time=time.time(),
            end_time=None,
            trace_id=trace_id,
            http=http_data)

        return segment
