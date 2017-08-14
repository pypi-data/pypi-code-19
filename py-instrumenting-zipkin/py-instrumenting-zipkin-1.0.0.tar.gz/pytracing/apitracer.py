from .trace import Trace


def request_tracer(function, **kwargs):
    """
    Decorator for tracing view/api request
    """
    operation_name = kwargs.get('operation', None)

    def wrap(request, *args, **kwargs):
        trace = Trace()
        trace.start(
            request,
            operation_name=function.__operation__,
            *args, **kwargs
        )

        response = function(request, *args, **kwargs)
        trace.set_operation_details(function, args, kwargs)
        trace.finish(response)
        return response

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    function.__operation__ = operation_name

    return wrap
