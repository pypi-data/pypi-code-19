from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework import exceptions


class UserProxy(object):
    """This class emulates a Django user model,
    acting as a mapping layer between the token
    payload and user data.
    """

    # Django expects these fields to exist on a "user model"
    pk = None
    is_authenticated = True
    is_anonymous = False

    def __init__(self,
                 email,
                 uuid,
                 groups,
                 primary_group):
        super(UserProxy, self).__init__()

        if groups is not None and not hasattr(groups, '__iter__'):
            msg = 'Groups field must be an iterable or null'
            raise exceptions.AuthenticationFailed(msg)

        self.email = email
        self.uuid = uuid
        self.groups = groups
        self.primary_group = primary_group

    def is_authenticated(self):
        return self.is_authenticated

    def is_anonymous(self):
        return self.is_anonymous


class MiniJWTAuthentication(JSONWebTokenAuthentication):

    def authenticate_credentials(self, payload):
        """If we've got this far it means that the JWT token has already been authenticated.
        Here we set request.user to a normal Python object instead of an Django model object read
        from the database.
        """

        email = payload.get('email')
        uuid = payload.get('user_id')
        groups = payload.get('groups')
        primary_group = payload.get('primary_group')

        return UserProxy(email=email,
                                uuid=uuid,
                                groups=groups,
                                primary_group=primary_group)

