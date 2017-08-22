# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

from __future__ import unicode_literals
import functools

from appdynamics.lang import get_args, urlparse
from . import HTTPConnectionInterceptor


def intercept_tornado_httpclient(agent, mod):
    import tornado.httputil
    import tornado.stack_context

    class AsyncHTTPClientInterceptor(HTTPConnectionInterceptor):
        def end_exit_call(self, exit_call, future):
            super(AsyncHTTPClientInterceptor, self).end_exit_call(exit_call, exc_info=future.exc_info())

        def _fetch(self, fetch, client, request, callback=None, raise_error=True, **kwargs):
            exit_call = None
            with self.log_exceptions():
                bt = self.bt
                if bt:
                    if not isinstance(request, mod.HTTPRequest):
                        request = mod.HTTPRequest(url=request, **kwargs)

                    url = urlparse(request.url)
                    port = url.port or ('443' if url.scheme == 'https' else '80')
                    backend = self.get_backend(url.hostname, port, url.scheme, request.url)
                    if backend:
                        exit_call = self.start_exit_call(bt, backend, operation=url.path)
                        request.headers = tornado.httputil.HTTPHeaders(request.headers)
                        correlation_header = self.make_correlation_header(exit_call)
                        if correlation_header is not None:
                            request.headers.add(*correlation_header)

            # The `raise_error` kwarg was added in tornado 4.1.  Passing it by name on versions
            # prior to this cause it to be included in the `**kwargs` parameter to `fetch`.  This
            # dict is passed directly to the `HTTPRequest` constructor, which does not have
            # `raise_error` in its signature and thus raises a TypeError.
            if 'raise_error' in get_args(fetch):
                future = fetch(client, request, callback=callback, raise_error=raise_error, **kwargs)
            else:
                future = fetch(client, request, callback=callback, **kwargs)
            future._callbacks.insert(0, functools.partial(tornado.stack_context.wrap(self.end_exit_call), exit_call))
            return future

    AsyncHTTPClientInterceptor(agent, mod.AsyncHTTPClient).attach('fetch', wrapper_func=None)
