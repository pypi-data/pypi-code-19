from coralillo import Engine
from flask import current_app

# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


class Coralillo(object):

    def __init__(self, app=None, config_prefix='REDIS'):
        self.app = app
        self.config_prefix = config_prefix
        self.redis = None
        self.lua = None

        if app is not None:
            self.init_app(app, config_prefix=config_prefix)

    def init_app(self, app, config_prefix=None):
        redis_url = app.config.get(
            '{0}_URL'.format(self.config_prefix), 'redis://localhost:6379/0'
        )

        engine = Engine(url = redis_url)
        self.lua = engine.lua
        self.redis = engine.redis
