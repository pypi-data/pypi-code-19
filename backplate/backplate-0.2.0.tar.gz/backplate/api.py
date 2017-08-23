
import re

from flask import Flask, Blueprint, jsonify
from flask_restful import Api
from flask_cors import CORS

from .errors import create_error_handler
from .mediatypes import create_json_output_handler, format_json_response
from .routing import bind_routes, create_routes

def errorsmap(errors):
    _errors = {}
    for error in errors:
        code = error['code']
        _errors[code] = error
    return _errors

def create_api(
    handle, name='api',
    routes=[], decorators=[], errors=[], mediatypes={},
    app=None, config=None, prefix='/v1',
    error_handler=None, json_output_handler=None, json_formatter=None
):
    """Returns flask app object"""

    bp = Blueprint(name, handle)

    _errors = errorsmap(errors)
    _mediatypes = mediatypes

    _json_formatter = json_formatter

    _error_handler = error_handler
    _json_output_handler = json_output_handler

    # default json_formatter
    if not json_formatter:
        _json_formatter = format_json_response

    # default error_handler
    if not error_handler:
        _error_handler = create_error_handler(_errors, _json_formatter)
    # default json_output_handler
    if not json_output_handler:
        _json_output_handler = create_json_output_handler(_json_formatter)
    # default mediatypes including json
    if not mediatypes:
        _mediatypes = {
            'application/json': _json_output_handler
        }

    class _Api(Api):
        def handle_error(self, e):
            return _error_handler(e)

    # create api from error handled class
    api = _Api(bp, decorators=decorators)
    api.catch_all_404s = True

    # register all mediatypes
    for mediatype in _mediatypes:
        handler = _mediatypes[mediatype]
        api.representation(mediatype)(handler)

    # bind routes for api
    bind_routes(api, create_routes(routes))

    if not app:
        app = Flask(handle)

    if config:
        app.config.from_object(config)

    app.api = api
    app.api_blueprint = bp

    # add api blueprint to app
    app.register_blueprint(bp, url_prefix=prefix)

    # add CORS origins headers to app, default '*'
    CORS(app, resources={
        r'' + re.escape(prefix) + r'/*': {
            'origins': app.config.get('CORS_ORIGINS', '*')
        }
    })

    # add index route
    @app.route('/')
    @app.route(prefix)
    def index():
        return jsonify(_json_formatter('OK', 200))

    # add healthcheck endpoint
    def healthcheck(f):
        @app.route('/healthcheck')
        def _healthcheck():
            return jsonify(f())

    app.healthcheck = healthcheck

    # add general error handling
    @app.errorhandler(Exception)
    def handle_bad_request(e):
        return _error_handler(e)

    return app

__all__ = ['create_api']
