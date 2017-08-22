import json
from flask import request, current_app, abort
from flask_login import login_user, current_user, logout_user
from ..models.error_model import ErrorModel
from ..models.user import User, Users
from ..util import NotFoundUserError, EchecAuthentification, Unauthorized,  Error, to_json, check_login

@to_json
def login():
    """
    autentification
    Returns user authentified

    :rtype: User
    """
    try:
        data = json.loads(request.data.decode())
        user = Users().get_user(id=data['id'])
        if user.check_password(data['password']):
            login_user(user, remember = True)
            return user.to_dict()
    except Error as e:
        pass
    raise Unauthorized()

@to_json
def logout():
    """
    logout autentification
    Returns user authentified

    :rtype: User
    """
    ret = current_user.to_dict()
    logout_user()
    return ret

@to_json
def current():
    """
    current user autentification
    Returns current user authentified

    :rtype: User
    """
    ret = current_user.to_dict()
    return ret

@to_json
def get_user(userId):
    """
    Find user by ID
    Returns a user
    :param userId: ID of userr that needs to be fetched
    :type userId: str

    :rtype: User
    """
    if not current_user.in_groups("admin") and userId != current_user.get_id():
        raise Unauthorized()
    return Users().get_user(id=userId).to_dict()

@to_json
def set_user(userId):
    """
    Updates a user with form data
    update user by Id
    :param userId: ID of user that needs to be updated
    :type userId: str
    :param body: User object that needs to be updated
    :type body: dict | bytes

    :rtype: None
    """
    data = json.loads(request.data.decode())
    if userId != data['id']:
        raise Error(status=405, title='invalid INPUT', type='RG-003', detail='userId is not compatible with user object')
    user = User().from_dict(data)
    Users().set_user(user)
    return user.to_dict()

@to_json
def add_user():
    """
    add user
    Returns user created

    :rtype: User
    """
    data = json.loads(request.data.decode())
    new_user = User().from_dict(data)
    Users().add_user(new_user)
    return new_user.to_dict()

