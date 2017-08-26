
from backplate_auth.exceptions import (
    AuthInvalidTokenPayloadError,
    AuthInvalidSessionError
)

class AuthTokenSessionsBase:

    # Required overrides

    def check_session(self, session, user_id):
        """
        Required override!
        Return boolean after checking session with database.
        Returning False will cause a validation error.
        """
        raise NotImplementedError

    def get_session(self, user_id):
        """
        Required override!
        Return int or string token to correspond as a handler for a session.
        Returning None will most probably invalidate the token.
        """
        raise NotImplementedError

    # Optional overrides

    def get_token_session(self, token):
        """
        Optional override.
        Returns session from the given token.
        Returning None may cause errors.
        """
        payload = self.get_token_payload(token) or {}
        session = payload.get('ssn')
        return session

    def check_token_payload_session(self, payload):
        """
        Optional override.
        Returns True after passing all checks, otherwises raises.
        Returning False will cause a validation error.
        """
        session = payload.get('ssn')
        if not session:
            raise AuthInvalidTokenPayloadError(
                "Token 'ssn' missing from payload")
        user_id = payload.get('uid')
        if not self.check_session(session, user_id):
            raise AuthInvalidSessionError(
                "Token 'ssn' is invalid session")

        return True

    def create_token_payload_session(self, payload, session):
        """
        Optional override.
        Returns payload dictionary after injecting the session.
        """
        payload['ssn'] = session
        return payload

    # Modular overrides

    def check_token_payload(self, payload):
        """
        Advanced override.
        Modular override that binds over AuthFlowBase.check_token_payload.
        Helper override to mount check_token_payload_session to AuthFlowBase.
        """
        if not self.check_token_payload_session(payload):
            return False

        return True

    def create_token_payload(self, user_id):
        """
        Advanced override.
        Modular override that bind over AuthFlowBase.create_token_payload.
        Helper override to inject session into payload.
        """
        payload = super().create_token_payload(user_id)
        session = self.get_session(user_id)
        payload = self.create_token_payload_session(payload, session)
        return payload


__all__ = ['AuthTokenSessionsBase']
