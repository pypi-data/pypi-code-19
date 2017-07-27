from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from rest_framework import authentication, exceptions

class KongDownstreamAuthHeadersAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        user_id = request.META.get('HTTP_X_AUTHENTICATED_USERID', None)
        if user_id is not None:
            user = get_user_model()(id=user_id, username=user_id)
            return (user, None)
        else:
            user = AnonymousUser()
            raise exceptions.AuthenticationFailed('User not authenticated')


