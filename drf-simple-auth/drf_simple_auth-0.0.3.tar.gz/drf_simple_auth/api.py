from __future__ import absolute_import, unicode_literals

import re

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .api_exceptions import (
    InvalidEmailOrPasswordAPIException, InvalidEmailUsernameAPIException,
    UsernameAlreadyTakenAPIException
)
from .models import AuthToken


class AuthLogin(APIView):

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        device_id = request.data.get('device_id') or ''

        if not username or not password:
            return Response(
                {'error': 'Missing username or password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            username=username.lower(), password=password
        )
        if not user:
            raise InvalidEmailOrPasswordAPIException()

        auth_token, _ = AuthToken.objects.get_or_create(
            user=user, device_id=device_id
        )

        return Response({'token': auth_token.key})


class AuthSignup(APIView):
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        device_id = request.data.get('device_id') or ''

        if not username or not password:
            return Response(
                {'error': 'Missing username or password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if getattr(settings, 'CHECK_USERNAME_IS_EMAIL', False):
            # Validate username is an email address
            if not AuthSignup.EMAIL_REGEX.match(username):
                raise InvalidEmailUsernameAPIException()

        try:
            user = get_user_model().objects.create_user(
                username.lower(), email=username.lower(),
                password=password
            )
        except IntegrityError:
            raise UsernameAlreadyTakenAPIException()

        auth_token, _ = AuthToken.objects.get_or_create(
            user=user, device_id=device_id
        )

        return Response({'token': auth_token.key}, status=status.HTTP_201_CREATED)
