from flask import Flask
from werkzeug.utils import find_modules, import_string

from .response import StatusCode, ApiResponse, ApiError


class ApiApp(Flask):
    def make_response(self, rv):
        if isinstance(rv, ApiResponse):
            return rv.to_flask_response()
        return Flask.make_response(self, rv)


def register_apis(app):
    for name in find_modules('lightflow_rest.api'):
        mod = import_string(name)
        if hasattr(mod, 'api'):
            app.register_blueprint(mod.api)


def register_error_handlers(app):
    app.register_error_handler(ApiError, lambda err: err.to_flask_response())
    app.register_error_handler(StatusCode.NotFound,
                               lambda err: ApiError(
                                   StatusCode.NotFound,
                                   'The requested endpoint does not exist').
                               to_flask_response())
    app.register_error_handler(StatusCode.MethodNotAllowed,
                               lambda err: ApiError(
                                   StatusCode.MethodNotAllowed,
                                   'The HTTP method is not allowed for this endpoint').
                               to_flask_response())


def create_app(config):
    app = ApiApp(__name__)

    app.config.update(config.extensions['rest'])
    app.config['LIGHTFLOW'] = config

    register_apis(app)
    register_error_handlers(app)

    return app
