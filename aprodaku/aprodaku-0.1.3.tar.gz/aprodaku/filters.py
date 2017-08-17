def methods (*allowed_methods):
    import io
    allowed_methods = list(allowed_methods)
    for allowed_method in allowed_methods:
        if not isinstance(allowed_method, str):
            error = TypeError("allowed method: exepcted {}".format(str.__name__))
            error.actual_type_name = type(allowed_method).__name__
            error.actual_value = allowed_method
            raise error
    def actual_decorator (function):
        def actual_filter (method, request_uri, headers, body_stream):
            if method not in allowed_methods:
                return 405, {"Content-Type": "text/plain", "Allow": str.join(",", allowed_methods)}, io.BytesIO(("Method '" + method + "' not allowed\n").encode("ascii"))
            else:
                return function(method, request_uri, headers, body_stream)
        return actual_filter
    return actual_decorator
