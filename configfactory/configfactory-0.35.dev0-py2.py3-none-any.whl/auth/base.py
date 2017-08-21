from typing import Optional

from django.core.exceptions import ObjectDoesNotExist
from django.middleware.csrf import rotate_token

from configfactory.auth.models import AnonymousUser, AuthUser, User

AUTH_SESSION_KEY = 'userid'


def login(request, user):
    """
    Login user.
    """
    if user is None:
        user = request.user

    if AUTH_SESSION_KEY in request.session:
        if request.session[AUTH_SESSION_KEY] != user.username:
            request.session.flush()
    else:
        request.session.cycle_key()

    request.session[AUTH_SESSION_KEY] = user.username

    if hasattr(request, 'user'):
        request.user = user
    rotate_token(request)


def logout(request):
    """
    Logout user.
    """
    request.session.flush()
    if hasattr(request, 'user'):
        request.user = AnonymousUser()


def authenticate(username, password) -> Optional[User]:
    """
    Authenticate user.
    """
    user = User.objects.find(username)
    if user:
        if user.check_password(password) and user.is_active:
            return user
    return None


def get_user(request) -> AuthUser:
    """
    Get user by current request.
    """

    if AUTH_SESSION_KEY in request.session:
        username = request.session[AUTH_SESSION_KEY]
        try:
            return User.objects.get(username)
        except ObjectDoesNotExist:
            pass
    return AnonymousUser()
