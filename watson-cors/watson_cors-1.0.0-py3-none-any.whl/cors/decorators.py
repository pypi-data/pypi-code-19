# -*- coding: utf-8 -*-
from watson.cors import utils


def cors(
        func=None,
        **cors_kwargs):
    """Adds CORS headers to a response from a controller.

    The order of inheritance of options used is as follows:

        1. The default configuration (watson.cors.config.defaults)
        2. The application configuration
        3. The route configuration (specify the arguments in the `options`
           property)
        4. The decorator arguments

    See https://developer.mozilla.org/en-US/docs/Web/HTTP/Access_control_CORS
    for additional information about valid values for each argument.

    Args:
        allow_origin (list|string): The allowed origin(s) for the request
        allow_credentials (boolean): Whether or not credentials are allowed
        allow_methods (list): The HTTP request methods that are allowed
        allow_headers (list): The HTTP headers that are allowed
        expose_headers (list): The HTTP headers which should be exposed
        max_age (integer): The length of time in seconds the OPTIONS response
                           can be cached
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            route = self.event.params['context']['route_match'].route
            conf = utils.generate_cors_config(
                self.container,
                route,
                **cors_kwargs)
            utils.process_cors(
                self.request,
                self.response, **conf)
            return func(self, **kwargs)
        return wrapper
    return decorator(func) if func else decorator
