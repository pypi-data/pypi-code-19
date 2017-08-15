from flask import Blueprint, redirect, url_for, abort
from flask_login import current_user
from pyedu.models import Level

stud = Blueprint('stud', __name__)

from . import views


@stud.before_request
def before_request():
    """
    Any Request in the stud Blueprint will be checked for authentification and at least STUDENT role
    access level before handling the request.

    :return:
    """
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))
    if not current_user.has_level(Level.STUDENT):
        return abort(403)