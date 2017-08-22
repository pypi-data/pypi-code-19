from __future__ import unicode_literals
from auth_roles import *
from jose.jwt import get_unverified_claims

from wellaware._compat import string_types


class Token(object):

    _audience = None
    _issuer = None
    _subject = None
    _created = None
    _expiration = None
    _tenant_name = None
    _timezone = None
    _tenant_id = None
    _tenant_uuid = None
    _subject_id = None
    _username = None
    _email = None
    _given_name = None
    _family_name = None
    _roles = []
    _permissions = []
    _impersonation = None
    _legacy_token = None
    _jwt = None

    def __init__(self, jwt=None, audience=None, issuer=None, subject=None, created=None, expiration=None,
                 tenant_name=None, timezone=None, tenant_id=None, tenant_uuid=None, subject_id=None, username=None,
                 email=None, given_name=None, family_name=None, roles=None, permissions=None, impersonation=None,
                 legacy_token=None):

        if jwt is not None:
            claims = get_unverified_claims(jwt)
            self._jwt = jwt
            self._audience = claims.get('aud', None)
            self._issuer = claims.get('iss', None)
            self._subject = claims.get('sub', None)
            self._created = claims.get('iat', None)
            self._expiration = claims.get('exp', None)
            self._tenant_name = claims.get('tname', None)
            self._timezone = claims.get('zoneinfo', None)
            self._tenant_id = claims.get('tid', None)
            self._tenant_uuid = claims.get('tuuid', None)
            self._subject_id = claims.get('sid', None)
            self._username = claims.get('username', None)
            self._email = claims.get('email', None)
            self._given_name = claims.get('given_name', None)
            self._family_name = claims.get('family_name', None)
            rls_claim = claims.get('rls', [])
            if isinstance(rls_claim, string_types):
                rls_claim = rls_claim.split(',')
            self._roles = rls_claim
            prms_claim = claims.get('prms', [])
            if isinstance(prms_claim, string_types):
                prms_claim = prms_claim.split(',')
            self._permissions = prms_claim
            self._impersonation = claims.get('impr', None)
            self._legacy_token = claims.get('wstk', None)
        else:  # pragma: no cover
            self._jwt = jwt
            self._audience = audience
            self._issuer = issuer
            self._subject = subject
            self._created = created
            self._expiration = expiration
            self._tenant_name = tenant_name
            self._timezone = timezone
            self._tenant_id = tenant_id
            self._tenant_uuid = tenant_uuid
            self._subject_id = subject_id
            self._username = username
            self._email = email
            self._given_name = given_name
            self._family_name = family_name
            self._roles = roles if not None else []
            self._permissions = permissions if not None else []
            self._impersonation = impersonation
            self._legacy_token = legacy_token

    @property
    def jwt(self):
        return self._jwt

    @property
    def audience(self):
        return self._audience

    @property
    def issuer(self):
        return self._issuer

    @property
    def subject(self):
        return self._subject

    @property
    def created(self):
        return self._created

    @property
    def expiration(self):
        return self._expiration

    @property
    def tenant_name(self):
        return self._tenant_name

    @property
    def timezone(self):
        return self._timezone

    @property
    def tenant_id(self):
        return self._tenant_id

    @property
    def tenant_uuid(self):
        return self._tenant_uuid

    @property
    def subject_id(self):
        return self._subject_id

    @property
    def username(self):
        return self._username

    @property
    def email(self):
        return self._email

    @property
    def given_name(self):
        return self._given_name

    @property
    def family_name(self):
        return self._family_name

    @property
    def roles(self):
        return self._roles

    def has_role(self, role_name):
        return role_name in self._roles

    @property
    def is_admin(self):
        return self.has_role(AuthRoles.ROLE_ADMIN) or self.has_role(AuthRoles.ROLE_WA_ADMIN)

    @property
    def is_controller(self):
        return self.has_role(AuthRoles.ROLE_CONTROLLER)

    @property
    def permissions(self):
        return self._permissions

    @property
    def impersonation(self):
        return self._impersonation

    @property
    def legacy_token(self):
        return self._legacy_token


__all__ = ['Token']