from sanic.response import json
from sanic.views import HTTPMethodView


View = HTTPMethodView
Json = json

def Qry(req):
    return req.raw_args or {}

def Doc(req):
    return req.json or {}
