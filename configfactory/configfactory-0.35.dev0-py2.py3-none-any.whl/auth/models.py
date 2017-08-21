import abc

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ObjectDoesNotExist
from django.utils.functional import cached_property


class AuthUser(abc.ABC):

    @property
    @abc.abstractmethod
    def is_authenticated(self):
        pass

    @property
    @abc.abstractmethod
    def is_active(self):
        pass

    @property
    @abc.abstractmethod
    def is_admin(self):
        pass

    @abc.abstractmethod
    def has_perm(self, perm):
        pass


class AnonymousUser(AuthUser):

    def __str__(self):
        return 'AnonymousUser'

    @property
    def is_authenticated(self):
        return False

    @property
    def is_admin(self):
        return False

    @property
    def is_active(self):
        return False

    def has_perm(self, perm):
        return False


class UserManager:

    @cached_property
    def _users(self):
        return self._load()

    def _load(self):
        """
        Load users.
        """

        users = {}

        for user_data in getattr(settings, 'USERS', []):
            username = user_data['username']
            password = user_data.get('password')
            is_active = user_data.get('is_active', True)
            is_admin = user_data.get('is_admin', False)
            permissions = user_data.get('permissions')
            user = User(
                username=username,
                password=password,
                is_active=is_active,
                is_admin=is_admin,
                permissions=permissions
            )
            users[username] = user

        return users

    def all(self):
        return list(self._users.values())

    def get(self, username):
        user = self.find(username)
        if user is None:
            raise ObjectDoesNotExist(
                'User `{username}` does not exist.'
            )
        return user

    def find(self, username):
        return self._users.get(username)


class User(AuthUser):

    objects = UserManager()

    def __init__(self,
                 username,
                 password=None,
                 is_active=True,
                 is_admin=False,
                 permissions=None):

        self.username = username
        self.password_hash = None
        self._is_active = is_active
        self._is_admin = is_admin

        if permissions is None:
            permissions = []
        self.permissions = permissions

        if password:
            self.set_password(password)

    def __str__(self):
        return self.username

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self._is_active

    @property
    def is_admin(self):
        return self._is_admin

    def set_password(self, password):
        self.password_hash = make_password(password)

    def check_password(self, password):
        return check_password(password, self.password_hash)

    def has_perm(self, perm: str):
        if self.is_admin:
            return True
        if perm not in self.permissions and perm.endswith(':read'):
            write_perm = perm.replace(':read', ':write')
            if write_perm in self.permissions:
                self.permissions.append(perm)
        return perm in self.permissions
