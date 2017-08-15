from flask import Blueprint, abort
from flask_login import current_user
from pyedu.models import Level

teach = Blueprint('teach', __name__)

from . import views

@teach.before_request
def before_request():
    if not current_user.has_level(Level.TEACHER):
        return abort(403)