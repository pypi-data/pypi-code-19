from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_login import LoginManager
from flask_migrate import Migrate
from pyedu.config import config


# instantiate Bootstrap and moment.js and SQLAlchemy
bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate(db=db)

# define an application factory
def app_factory(config_name):
    """
    Returns an instance of the app using the given config.

    :param config_name:
    :return:
    """
    print('Creating App with config: %s' % config_name)
    app = Flask(__name__)

    # set the config
    app.config.from_object(config[config_name])
    # register the app
    config[config_name].init_app(app)

    # initialize all extensions
    bootstrap.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app)

    # make the login settings
    from pyedu.models import AnonymousUser
    login_manager.anonymous_user = AnonymousUser
    login_manager.login_view = 'main.login'

    # register the main Blueprint routes for this app instance
    from pyedu.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # register the student Blueprint routes for this app instance
    from pyedu.student import stud as student_blueprint
    app.register_blueprint(student_blueprint, url_prefix='/s')

    from pyedu.teacher import teach as teacher_blueprint
    app.register_blueprint(teacher_blueprint, url_prefix='/t')

    return app
