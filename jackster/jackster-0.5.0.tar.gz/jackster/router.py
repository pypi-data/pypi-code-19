from werkzeug.serving import run_simple
from .request import Request
from .response import Response
from .chain import Chain
import re


def error(code):
    def func(req, res, nxt, *args, **kwargs):
        res.status(code).html('Error {}'.format(code))
        nxt(*args, **kwargs)
    return func


default_errors = {
    code: error(code)
    for code in (404, 405, 500)
}


def NO_NEXT(*args, **kwargs):
    pass


class Router:

    def __init__(self):
        self.handlers = []

    # Methods to add handlers for every http request method
    def options(self, path, handler=r'^$'):
        return self.method('OPTIONS', path, handler)

    def get(self, path, handler=r'^$'):
        return self.method('GET', path, handler)

    def head(self, path, handler=r'^$'):
        return self.method('HEAD', path, handler)

    def post(self, path, handler=r'^$'):
        return self.method('POST', path, handler)

    def put(self, path, handler=r'^$'):
        return self.method('PUT', path, handler)

    def patch(self, path, handler=r'^$'):
        return self.method('PATCH', path, handler)

    def delete(self, path, handler=r'^$'):
        return self.method('DELETE', path, handler)

    def trace(self, path, handler=r'^$'):
        return self.method('TRACE', path, handler)

    def connect(self, path, handler=r'^$'):
        return self.method('CONNECT', path, handler)

    # Method to add handlers for errors
    def error(self, code, path, handler=r'^'):
        return self.method(code, path, handler)

    # Method to add handlers that will be used for every method
    def use(self, path, handler=r'^'):
        return self.method('USE', path, handler)

    def method(self, method, path, handler=r'^$'):
        if isinstance(method, (list, tuple)):
            for m in method:
                self.method(m, path, handler)
            return self
        if isinstance(handler, str):
            return self.method(method, handler, path)
        self.handlers.append((method, re.compile(path), handler))
        return self

    def match(self, method, path):
        handler, args, kwargs = Chain(), (), {}
        found, exists = False, False
        for method_, path_, handler_ in self.handlers:
            match = path_.search(path)
            if match and method_ in (method, 'USE'):
                args_ = list(match.groups())
                for i in sorted(
                    (i for _, i in path_.groupindex.items()),
                    reverse=True
                ):
                    args_.pop(i - 1)
                args += tuple(args_)
                kwargs.update(match.groupdict())
                if method_ != 'USE':
                    found, exists = True, True
                if isinstance(handler_, Router):
                    handler__, args_, kwargs_ = handler_.match(
                        method, path[:match.start()] + path[match.end():]
                    )
                    if handler__ is not None:
                        exists = True
                        if handler__:
                            found = True
                            handler.extend(handler__)
                            args += args_
                            kwargs.update(kwargs_)
                else:
                    handler.append(handler_)
            elif match and not isinstance(method_, int):
                exists = True
        return (
            ((handler if found else Chain()) if exists else None),
            args, kwargs
        )

    @Request.application
    def __call__(self, req):
        path = req.path.rstrip('/')
        handler, args, kwargs = self.match(req.method, path)
        # Catch 404 errors
        if handler is None:
            handler, args, kwargs = self.match(404, path)
            if handler is None or not handler:
                handler, args, kwargs = default_errors[404], (), {}
        # Catch 405 errors
        if not handler:
            handler, args, kwargs = self.match(405, path)
            if not handler:
                handler, args, kwargs = default_errors[405], (), {}
        # Catch 500 errors
        res = Response()
        try:
            handler(req, res, NO_NEXT, *args, **kwargs)
        except Exception as e:
            handler, args, kwargs = self.match(500, path), (e,), {}
            res = Response()
            try:
                handler(req, res, NO_NEXT, *args, **kwargs)
            except Exception as e:
                handler, args, kwargs = default_errors[500], (e,), {}
                res = Response()
                handler(req, res, NO_NEXT, *args, **kwargs)
        return res.res

    def listen(self, host='localhost', port=8000):
        run_simple(host, port, self, use_reloader=True)
