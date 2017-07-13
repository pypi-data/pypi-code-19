import os
import sys

def main (function):
    import io
    from traceback import format_exc
    try:
        from steov import format_exc
        method, uri, headers, body_stream = get_request_from_cgi()
        status, headers, body_stream = function(method, uri, headers, body_stream)
        status, headers, body_stream = validate_response(status, headers, body_stream)
    except Exception as ex:
        status = 500
        if os.environ.get("HTTP_X_APRODAKU_SHOW_STACKTRACE"):
            body = format_exc().encode("utf-8")
        else:
            body = b"Internal Server Error\n"
        headers = {
            "Content-Type": "text/plain;charset=utf-8",
            "Content-Length": str(len(body)),
        }.items()
        body_stream = io.BytesIO(body)

    sys.stdout.buffer.write("Status: {}\r\n".format(status).encode("ascii"))
    for k, v in headers:
        sys.stdout.buffer.write("{}: {}\r\n".format(k, v).encode("utf-8"))
    sys.stdout.buffer.write(b"\r\n")
    if body_stream is not None:
        try:
            while True:
                block = body_stream.read(4096)
                if not block:
                    break
                sys.stdout.buffer.write(block)
        except Exception:
            # TODO handle this better. help:
            # https://stackoverflow.com/questions/15305203/what-to-do-with-errors
            pass

def get_request_from_cgi ():
    method = os.environ["REQUEST_METHOD"]
    uri = os.environ["REQUEST_URI"]
    headers = []
    prefix = "HTTP_"
    for k, v in os.environ.items():
        if not k.startswith(prefix):
            continue
        header_name = "-".join(map(str.capitalize, k[len(prefix):].split("_")))
        headers.append((header_name, v))
    body_stream = sys.stdin.buffer
    return method, uri, headers, body_stream

_header_name_pattern = None
_header_value_pattern = None
def validate_response (status, headers, body_stream):
    import re
    global _header_name_pattern
    global _header_value_pattern
    if _header_name_pattern is None:
        _header_name_pattern = re.compile(r"\A\S+\Z")
    if _header_value_pattern is None:
        _header_value_pattern = re.compile(r"\A[^\b\r\n]*\Z")

    if not isinstance(status, int):
        error = TypeError("status: expected {}".format(int.__name__))
        error.actual_type_name = type(status).__name__
        error.actual_value = status
        raise error
    if not status in range(100, 1000):
        error = ValueError("status: must be in {}".format(range(100, 1000)))
        error.actual_value = status
        raise error
    if isinstance(headers, dict):
        headers = headers.items()
    new_headers = list()
    for name, value in headers:
        if not isinstance(name, str):
            error = TypeError("header name: exepcted {}".format(str.__name__))
            error.actual_type_name = type(name).__name__
            error.actual_value = name
            raise error
        if not _header_name_pattern.search(name):
            error = ValueError("header name: must match regex {}".format(_header_name_pattern.pattern))
            error.actual_value = name
            raise error
        value = str(value)
        if not _header_value_pattern.search(value):
            error = ValueError("header value: must match regex {}".format(_header_value_pattern.pattern))
            error.actual_value = value
            raise error
        new_headers.append((name, value))
    if body_stream is not None and not callable(body_stream.read):
        raise TypeError("body_stream.read: not callable")
    return status, headers, body_stream
