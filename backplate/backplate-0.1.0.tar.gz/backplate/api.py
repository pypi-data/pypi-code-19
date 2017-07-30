
import re

from flask import Blueprint
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
    endpoints=[], decorators=[], errors=[], mediatypes={},
    app=None, prefix='/v1',
    error_handler=None, json_output_handler=None, json_formatter=None
):
    """Returns flask blueprint and flask_restful Api object"""

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
    bind_routes(api, create_routes(endpoints))

    if app:
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

        # add general error handling
        @app.errorhandler(Exception)
        def handle_bad_request(e):
            return _error_handler(e)

        return app

    return bp, api

__all__ = ['create_api']
