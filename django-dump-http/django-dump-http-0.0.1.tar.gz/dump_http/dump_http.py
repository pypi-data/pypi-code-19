import re
import time
import os, errno
from django.conf import settings

# WARNING: The order of headers, quoting, and probably lettercase is broken
def reconstruct_request_or_response(request_or_response, kind):
    regex_http_ = re.compile(r'^HTTP_.+$')
    regex_content_type = re.compile(r'^CONTENT_TYPE$')
    regex_content_length = re.compile(r'^CONTENT_LENGTH$')
    regex_del_http = re.compile(r'^HTTP_')

    META = request_or_response.META if kind == 'request' else request_or_response
    request_headers = {}
    for header in META:
        header = str(header)  # necessary for HttpResponse objects
        if regex_http_.match(header) or regex_content_type.match(header) or regex_content_length.match(header):
            header2 = regex_del_http.sub('', header)
            header2 = header2.replace('_', '-')
            request_headers[header2] = META[header]

    # FIXME: quote headers
    return "\r\n".join([h+': '+d for (h, d) in request_headers.items()])

start_time = int(time.time())

class DumpHTTPMiddleware(object):
    # One-time configuration and initialization.
    def __init__(self, get_response):
        self.get_response = get_response
        self.serial = 0

    def __call__(self, request):
        response = self.get_response(request)

        request_str = reconstruct_request_or_response(request, 'request')
        # response_str = reconstruct_request_or_response(response, 'response')
        response_str = response.serialize().decode("utf-8")

        # WARNING: Protocol (such as HTTP/1.1) is missing
        request_str = "%s %s\r\n%s" % (request.method, request.path, request_str)
        request_str += "\r\n\r\n" + request.body.decode("utf-8")
        # response_str += "\r\n\r\n" + response.content.decode("utf-8")

        cur_time = int(time.time())
        try:
            dir = settings.DUMP_HTTP_DIR
        except AttributeError:
            dir = 'dump.out'

        base_name = "%s/%d-%d-%d" % (dir, start_time, cur_time, self.serial)

        try:
            os.makedirs(dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        with open("%s.1" % base_name, "w") as request_file:
            request_file.write(request_str)
        with open("%s.2" % base_name, "w") as response_file:
            response_file.write(response_str)

        self.serial += 1

        return response