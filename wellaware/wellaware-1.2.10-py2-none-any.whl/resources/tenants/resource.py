from __future__ import unicode_literals

from wellaware.base import BaseResource
from wellaware.resources.tenants.models import Tenant


class Tenants(BaseResource):

    @classmethod
    def endpoint(cls):
        return '/tenants'

    @classmethod
    def endpoint_single(cls):
        return '/tenants/{id}'

    @classmethod
    def entity_class(cls):
        return Tenant

    @classmethod
    def create(cls, token, tenant, parameters=None):
        cls.validate_is_entity(tenant, Tenant)
        return cls._create(token, tenant, parameters=parameters)

    @classmethod
    def retrieve_one(cls, token, tenant_id, parameters=None):
        tenant_id = cls.get_entity_id(tenant_id, Tenant)
        return cls._retreive_one(token, tenant_id, parameters=parameters)

    @classmethod
    def retrieve_all(cls, token, parameters=None):
        return cls._retrieve_all(token, parameters=parameters)

    @classmethod
    def me(cls, token, parameters=None):
        return cls._retreive_one(token, None, ids={'id': 'me'}, parameters=parameters)

    @classmethod
    def update(cls, token, tenant, parameters=None):
        cls.validate_is_entity(tenant, Tenant)
        return cls._update(token, tenant, parameters=parameters)

    @classmethod
    def delete(cls, token, tenant_id, parameters=None):
        tenant_id = cls.get_entity_id(tenant_id, Tenant)
        return cls._delete(token, tenant_id, parameters=parameters)

__all__ = ['Tenant', 'Tenants']
