from flask import current_app, g
from .controller import blueprint

from fuser import templates


# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack
import jinja2
import os

class Fuser(object):

    def __init__(self, app=None, after_login_dest='/dashboard'):
        self.app = app
        self.after_login_dest = after_login_dest

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # app.config.setdefault('SQLITE3_DATABASE', ':memory:')
        
        # Use the newstyle teardown_appcontext if it's available,
        # otherwise fall back to the request context

        # IDEA: does app have config here? Could set app level variables to make things
        #  like "override_login_url" possible.


        extra_folders = jinja2.ChoiceLoader([
            app.jinja_loader,
            jinja2.FileSystemLoader(os.path.dirname(templates.__file__)),
        ])
        app.jinja_loader = extra_folders

        app.register_blueprint(blueprint)
        self._init_extension()


    def _init_extension(self):
        if not hasattr(self.app, 'extensions'):
            self.app.extensions = dict()

        admins = self.app.extensions.get('fuser', [])

        for p in admins:
            if p.endpoint == self.endpoint:
                raise Exception(u'Cannot have two Fuser() instances with same'
                                u' endpoint name.')

            if p.url == self.url and p.subdomain == self.subdomain:
                raise Exception(u'Cannot assign two Fuser() instances with same'
                                u' URL and subdomain to the same application.')

        admins.append(self)
        self.app.extensions['fuser'] = admins