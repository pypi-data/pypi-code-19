from .trace import Trace


class PyTraceMiddleware(object):
    """
    Middleware to trace incomming requests
    """
    def __init__(self):
        self.trace = Trace()
        print(id(self.trace))

    def process_request(self, request):
        self.trace.start(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        self.trace.set_operation_details(
            view_func, view_args, view_kwargs)

    def process_response(self, request, response):
        self.trace.finish(response)
        return response
