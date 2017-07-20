"""
:mod:`zsl_jwt.auth.service`
---------------------------

The abstraction of authentication service and user information.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from abc import ABCMeta
from abc import abstractmethod
from builtins import *  # NOQA
from typing import Any  # NOQA
from typing import Callable  # NOQA
from typing import Generic  # NOQA
from typing import List  # NOQA
from typing import Set  # NOQA
from typing import Tuple  # NOQA
from typing import TypeVar  # NOQA

from zsl.db.model.app_model import AppModel

from zsl_jwt.codec import decode
from zsl_jwt.configuration import DEFAULT_PROFILE_NAME


class AuthenticationService(object):
    """
    The service used for verifying username and password and
    querying the user information.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def verify_password(self, username, password):
        # type:(str, str)->bool
        """Verifies if the username, password combination is valid.
        Returns true iff it is, False otherwise. It should not raise
        exceptions."""
        pass

    @abstractmethod
    def get_user_information(self, username):
        # type:(str)->Tuple[List[str], Any]
        """
        Returns the user information for the given username.
        :param username:
        :return: Tuple with the first element being the list of roles
                 (list of strings) and a user information, may be ``None``.
        """
        pass


T = TypeVar('T')


class StandardUserInformation(AppModel, Generic[T]):
    """Standard user information - contains username,
    roles (list of strings) and a user object, if wanted (may be ``None``)"""

    def __init__(self, username, roles, user_object):
        # type:(str, List[str], T)->None
        self._username = username
        self._roles = set(roles)
        self._user_object = user_object

        super(StandardUserInformation, self).__init__({})

    def get_attributes(self):
        return {
            'roles': list(self._roles),
            'username': self.username,
            'user_object': self._user_object
        }

    @property
    def username(self):
        # type: ()->str
        return self._username

    @property
    def roles(self):
        # type: ()->Set[str]
        return self._roles

    def is_in_role(self, role):
        # type:(str)->bool
        return role in self._roles

    @property
    def user_object(self):
        # type:()->T
        return self._user_object


def create_standard_user_information(username, roles, user_object):
    # type: (str, List[str], Any)->StandardUserInformation
    """Creates the user information/representation from the given parameters."""
    return StandardUserInformation(username, roles, user_object)


def decode_to_standard_user_information(token, user_object_class=None, profile=DEFAULT_PROFILE_NAME):
    # type: (str, Callable)->StandardUserInformation
    """Creates the user information/representation from the given auth token."""
    payload = decode(token, profile)
    if user_object_class is not None:
        payload['user_object'] = user_object_class(payload['user_object'])
    return StandardUserInformation(**payload)
