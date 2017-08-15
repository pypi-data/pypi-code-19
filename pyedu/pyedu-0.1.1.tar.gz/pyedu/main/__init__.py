from flask import Blueprint, g
from pyedu.models import Level

main = Blueprint('main', __name__)

from . import views


@main.before_app_request
def before_app_request():
    # TODO: there should be a way better way to add the Level from models to the app
    g.Level = Level