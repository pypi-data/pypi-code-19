from rest_framework.authentication import TokenAuthentication


class SimpleAuthTokenAuthentication(TokenAuthentication):
    """
    Authenticate a user using a AuthToken
    """

    keyword = 'DToken'

    def get_model(self):
        if self.model is not None:
            return self.model
        from .models import AuthToken
        return AuthToken
