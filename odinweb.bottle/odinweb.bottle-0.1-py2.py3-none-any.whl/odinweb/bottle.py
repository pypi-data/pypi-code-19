"""
OdinWeb.Bottle API
~~~~~~~~~~~~~~~~~

Bottle implementation of the OdinWeb API interface.

Usage::
    
    import bottle
    from odinweb.bottle import Api
        
    app = bottle.Bottle()
    app.merge(
        Api(
            ApiVersion(
                UserApi(),
                version='v1
            )
        )
    )    

"""
from __future__ import absolute_import

from bottle import Route, response, request

from odinweb.api import ApiInterfaceBase
from odinweb.data_structures import PathNode


class RequestProxy(object):
    def __init__(self, r):
        self.GET = r.GET
        self.POST = r.POST
        self.headers = r.headers
        self.method = r.method
        self.request = r

    @property
    def body(self):
        return self.request.body.read()

    @property
    def host(self):
        return self.request.environ.get('HTTP_HOST')


class Api(ApiInterfaceBase):
    def __iter__(self):
        """
        Convenience iterator to simplify registration with Bottle using :func:`bottle.Bottle.merge`. 
        """
        return iter(self.routes())

    @property
    def plugins(self):
        # Placeholder to match the Bottle App API.
        return []

    def routes(self):
        return list(self.build_routes())

    def parse_node(self, node):
        if isinstance(node, PathNode):
            if node.type in ('re', 'int', 'float', 'path'):
                if node.type_args:
                    return "<{}:{}({})>".format(node.name, node.type, ', '.join(node.type_args))
                else:
                    return "<{}:{}>".format(node.name, node.type)
            else:
                return "<{}>".format(node.name)
        else:
            return str(node)

    def build_routes(self):
        for path, methods, callback in super(Api, self).build_routes():
            callback = self._bound_callback(callback)
            for method in methods:
                yield Route(self, path, method, callback)

    def _bound_callback(self, f):
        def callback(**kwargs):
            resp = f(RequestProxy(request), **kwargs)

            response.status = resp.status
            for k, v in resp.headers.items():
                response[k] = v

            return resp.body
        return callback
