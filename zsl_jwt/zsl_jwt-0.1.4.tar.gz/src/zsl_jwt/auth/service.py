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
from typing import List  # NOQA
from typing import Tuple  # NOQA

from zsl.db.model.app_model import AppModel


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


class StandardUserInformation(AppModel):
    """Standard user information - contains username,
    roles (list of strings) and a user object, if wanted (may be ``None``)"""
    def __init__(self, username, roles, user_object):
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
        return self._username

    @property
    def roles(self):
        return self._roles

    def is_in_role(self, role):
        return role in self._roles

    @property
    def user_object(self):
        return self._user_object


def create_standard_user_information(username, roles, user_object):
    # type: (str, List[str], Any)->StandardUserInformation
    """Creates the user information/representation from the given parameters."""
    return StandardUserInformation(username, roles, user_object)
