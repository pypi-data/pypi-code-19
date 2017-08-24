from django.conf import settings
from django.contrib.auth import get_user_model

from django.contrib.auth import login as django_login, authenticate, logout
#from django.contrib.auth.models import User

from django.contrib.auth import get_user_model
from django.middleware.csrf import rotate_token
from django.utils.crypto import constant_time_compare
from django.utils.module_loading import import_string
from django.utils.translation import LANGUAGE_SESSION_KEY

SESSION_KEY = '_auth_user_id'
BACKEND_SESSION_KEY = '_auth_user_backend'
HASH_SESSION_KEY = '_auth_user_hash'
REDIRECT_FIELD_NAME = 'next'


def _get_user_session_key(request):
    # This value in the session is always serialized to a string, so we need
    # to convert it back to Python whenever we access it.
    return get_user_model()._meta.pk.to_python(request.session[SESSION_KEY])


class MmogoUserBackEnd(object):
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except Exception as e:
            return None

    def authenticate(self, email=None, password=None):
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except Exception, e:
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                user.backend = settings.AUTHENTICATION_BACKENDS
                return user
        return None

    def user_can_authenticate(self, user):
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

    def login(self, request, email, password):
        user = self.authenticate(email, password)
        user.backend = settings.AUTHENTICATION_BACKENDS
        django_login(request, user)

    def mmogo_logout(self, request):
        request.session['usersession'] = ''
