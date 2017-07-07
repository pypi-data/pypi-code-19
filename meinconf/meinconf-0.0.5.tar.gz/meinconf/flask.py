from .config import Config


class FlaskConfig(Config):
    def __init__(self, app=None, app_name=None, root_path=None, defaults=None):
        """
        :param flask.Flask app: Flask application object. Sets remaining
            parameters if not explicitly given.
        :param str|unicode app_name: The name of the application.
            It will find environment variables for configuration
            by looking for the <name upper case>_CONFIG_KEY.  If
            no name is specified it uses the environment variable with
            name "APP_NAME".
        :param str|unicode root_path: Root path of the application to look for
            config files in
        :param dict defaults: Default configuration options
        """
        if app_name is None:
            app_name = app.name
        if root_path is None:
            root_path = app.root_path
        if defaults is None:
            defaults = app.config

        super(FlaskConfig, self).__init__(
            app_name=app_name,
            root_path=root_path,
            defaults=defaults,
        )

    def configure_flask_app(self, app):
        """
        Update Flask application configuration.

        :param flask.Flask app: Flask application object to configure.
        """
        app.config.update(self)

