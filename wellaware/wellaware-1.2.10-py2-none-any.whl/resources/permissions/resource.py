from __future__ import unicode_literals

from wellaware.base import BaseResource
from wellaware.resources.roles import Role
from wellaware.resources.permissions import Permission


class Permissions(BaseResource):

    @classmethod
    def endpoint(cls):
        return '/roles/{role_id}/permissions'

    @classmethod
    def endpoint_single(cls):
        return '/roles/{role_id}/permissions/{id}'

    @classmethod
    def entity_class(cls):
        return Permission

    @classmethod
    def create(cls, token, role_id, permission, parameters=None):
        role_id = cls.get_entity_id(role_id, Role)
        cls.validate_is_entity(permission, Permission)
        return cls._create(token, permission, parameters=parameters, ids={'role_id': role_id})

    @classmethod
    def retrieve_one(cls, token, role_id, permission_id, parameters=None):
        role_id = cls.get_entity_id(role_id, Role)
        permission_id = cls.get_entity_id(permission_id, Permission)
        return cls._retreive_one(token, permission_id, parameters=parameters, ids={'role_id': role_id})

    @classmethod
    def retrieve_all(cls, token, role_id, parameters=None):
        role_id = cls.get_entity_id(role_id, Role)
        return cls._retrieve_all(token, parameters=parameters, ids={'role_id': role_id})

    @classmethod
    def update(cls, token, role_id, permission, parameters=None):
        role_id = cls.get_entity_id(role_id, Role)
        cls.validate_is_entity(permission, Permission)
        return cls._update(token, permission, parameters=parameters, ids={'role_id': role_id})

    @classmethod
    def delete(cls, token, role_id, permission_id, parameters=None):
        role_id = cls.get_entity_id(role_id, Role)
        permission_id = cls.get_entity_id(permission_id, Permission)
        return cls._delete(token, permission_id, parameters=parameters, ids={'role_id': role_id})


__all__ = ['Permission', 'Permissions']
