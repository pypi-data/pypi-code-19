
from flask import request
from webargs import fields

from .jwt import JWT
from .exceptions import (
    AuthInvalidTokenError,
    AuthInvalidTokenPayloadError,
    AuthInvalidTokenUserError
)

class AuthTokenFlowBase:
    jwt_args = {}
    endpoint_args = {'token': fields.String()}

    def __init__(self):
        self.jwt = JWT(**self.jwt_args)

    # Required overrides

    def resolve_request_user_id(self):
        """
        Required override!
        Return a user id from the request object.
        Returning None will cause a validation error.
        """
        raise NotImplementedError

    def resolve_user_id(self, user_id):
        """
        Required override!
        Return an object that represents the user from database user_id.
        Returning None will cause a validation error.
        """
        raise NotImplementedError

    # Optional overrides

    def new_token(self, user_id):
        """
        Optional override.
        Return token from result of create_token_payload.
        Returning anything else will cause a token creation error.
        """
        payload = self.create_token_payload(user_id)
        return self.jwt.create(payload)

    def renew_token(self, token):
        """
        Optional override.
        Return token from result of get_token_payload.
        Returning anything else will cause a token creation error.
        """
        payload = self.get_token_payload(token)
        return self.jwt.create(payload)

    def create_token_payload(self, user_id):
        """
        Optional override.
        Return a dictionary containing at least the 'uid' of user.
        Returning anything else will cause a token creation error.
        """
        return {'uid': user_id}

    def check_token_payload(self, payload):
        """
        Optional override.
        Return a boolean after running additional validation checks.
        Returning False will cause a validation error.
        """
        return True

    def get_token_payload(self, token):
        """
        Optional override.
        Return a dictionary from the given token payload.
        Returning None will cause a validation error.
        """
        try:
            payload = self.jwt.parse(token)
        except Exception as e:
            raise AuthInvalidTokenError(str(e))
        return payload

    def get_token_user_id(self, token):
        """
        Optional override.
        Return a user id from the given token.
        Returning None will cause a validation error.
        """
        payload = self.get_token_payload(token) or {}
        user_id = payload.get('uid')
        return user_id

    def get_request_token(self):
        """
        Optional override.
        Return token from the request object.
        Returning None will cause a validation error.
        """
        token_header = request.headers.get('Authorization')
        token_arg = request.args.get('token')
        return token_header or token_arg

    # Advanced optional overrides

    def check_token(self, token):
        """
        Advanced override.
        Returns True after passing all checks, otherwise raises exceptions.
        Returning False will cause a validation error.
        """

        # token - validity check
        payload = self.get_token_payload(token)
        if not payload:
            raise AuthInvalidTokenError(
                "Token payload missing")

        # token - payload: uid field check
        user_id = self.get_token_user_id(token)
        if user_id is None:
            raise AuthInvalidTokenPayloadError(
                "Token 'uid' missing from payload")

        # token - payload: custom check
        if not self.check_token_payload(payload):
            raise AuthInvalidTokenPayloadError(
                "Token payload validation error")

        # system - user check
        if not self.resolve_user_id(user_id):
            raise AuthInvalidTokenUserError(
                "Token 'uid' is invalid user")

        return True

__all__ = ['AuthTokenFlowBase']
