from __future__ import unicode_literals

from wellaware.base import BaseResource
from wellaware.resources.roles import Role


class Roles(BaseResource):

    @classmethod
    def endpoint(cls):
        return '/roles'

    @classmethod
    def endpoint_single(cls):
        return '/roles/{id}'

    @classmethod
    def entity_class(cls):
        return Role

    @classmethod
    def create(cls, token, role, parameters=None):
        cls.validate_is_entity(role, Role)
        return cls._create(token, role, parameters=parameters)

    @classmethod
    def retrieve_one(cls, token, role_id, parameters=None):
        role_id = cls.get_entity_id(role_id, Role)
        return cls._retreive_one(token, role_id, parameters=parameters)

    @classmethod
    def retrieve_all(cls, token, parameters=None):
        return cls._retrieve_all(token, parameters=parameters)

    @classmethod
    def update(cls, token, role, parameters=None):
        cls.validate_is_entity(role, Role)
        return cls._update(token, role, parameters=parameters)

    @classmethod
    def delete(cls, token, role_id, parameters=None):
        role_id = cls.get_entity_id(role_id, Role)
        return cls._delete(token, role_id, parameters=parameters)


__all__ = ['Role', 'Roles']
