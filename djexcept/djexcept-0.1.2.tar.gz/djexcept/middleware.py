from django.conf import settings
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    # pre django 1.10 style middleware
    MiddlewareMixin = object

from .config import config
from .registration import _get_exception_handler_attrs


class ExceptionHandlingMiddleware(MiddlewareMixin):
    """
    A Django middleware responsible for djexcept's exception handling.
    """

    def __init__(self, *args, **kwargs):
        super(ExceptionHandlingMiddleware, self).__init__(*args, **kwargs)

    def process_exception(self, request, exc):
        if settings.DEBUG and config.disable_on_debug:
            # don't do anything
            return

        handler_kwargs = {}
        handler_kwargs.update(config.default_handler_kwargs)

        exc_cls = exc.__class__
        handler_attrs = _get_exception_handler_attrs(exc_cls)

        if handler_attrs is None:
            # we don't handle this kind of exception, pass it through
            return

        handler = handler_attrs.get("handler", config.default_handler)
        handler_kwargs.update(handler_attrs)

        # remove reserved attributes from kwargs
        for key in ("handler", "handle_subclasses",):
            try:
                del handler_kwargs[key]
            except KeyError:
                pass

        # finally, call the handler
        return handler(request, exc, **handler_kwargs)
