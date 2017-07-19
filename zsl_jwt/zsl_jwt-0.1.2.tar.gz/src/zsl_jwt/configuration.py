"""
:mod:`zsl_jwt.configuration`
----------------------------
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from builtins import *  # NOQA
from typing import Dict  # NOQA

from zsl.errors import ZslError

DEFAULT_PROFILE_NAME = 'default'
CLAIM_ISSUER = 'zsl_jwt'
CLAIM_AUDIENCE = 'zsl_jwt'
CLAIM_NOT_BEFORE = datetime.timedelta(seconds=0)
CLAIM_EXPIRATION = datetime.timedelta(hours=1)


class JWTConfiguration(object):
    """
    The main JWT configuration object. Consists of several token profiles
    used for encoding/decoding. See :class:`zsl_jwt.configuration.JWTProfile`.
    """

    def __init__(self, default_secret=None, default_profile=None,
                 profiles=None):
        # type:(str, JWTProfile, Dict[str, JWTProfile])->None
        if profiles is None:
            profiles = {}

        if DEFAULT_PROFILE_NAME not in profiles:
            if default_profile is None:
                if default_secret is None:
                    raise ZslError("JWT Secret or default profile not present.")
                default_profile = JWTProfile(default_secret, CLAIM_EXPIRATION,
                                             CLAIM_NOT_BEFORE, CLAIM_ISSUER,
                                             CLAIM_AUDIENCE)

            profiles[DEFAULT_PROFILE_NAME] = default_profile

        self._profiles = profiles

    def __getitem__(self, item):
        # type:(str)->JWTProfile
        return self._profiles[item]


class JWTProfile(object):
    """
    Each profile consits of its own
     - secret and all the JWT claims definitions:
     - audience: `str` - must match the audience in the decoding,
     - issuer name: `str` - just an information about the token issuer,
     - expiration: `datetime.timedelta` specifying when token becomes invalid,
     - not_before: `datetime.timedelta` specifying when token becomes valid.
    """

    def __init__(self, secret, expiration=None, not_before=None, issuer=CLAIM_ISSUER,
                 audience=CLAIM_AUDIENCE):
        # type:(str, datetime.timedelta, datetime.timedelta, str, str)->None
        if expiration is None:
            expiration = CLAIM_EXPIRATION
        if not_before is None:
            not_before = CLAIM_NOT_BEFORE
        self._secret = secret
        self._expiration = expiration
        self._not_before = not_before
        self._issuer = issuer
        self._audience = audience

    @property
    def secret(self):
        """Key/secret used for encryption."""
        return self._secret

    @property
    def issuer(self):
        """The issuer name. This is a standard JWT claim."""
        return self._issuer

    @property
    def audience(self):
        """The audience of the token for which the token is intended.
        This must match the audience used for decoding. This is a standard
        JWT claim."""
        return self._audience

    @property
    def expiration(self):
        """The time interval specifying when the token becomes invalid.
        The token is valid until time now + expiration.
        This is a standard JWT claim."""
        return self._expiration

    @property
    def not_before(self):
        """The time interval specifying when the token becomes valid.
        The token is valid from time now + not_before.
        This is a standard JWT claim."""
        return self._not_before
