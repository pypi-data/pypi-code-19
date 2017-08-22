from __future__ import unicode_literals

from wellaware.base import BaseResource
from wellaware.resources.sites.models import Site


class Sites(BaseResource):

    @classmethod
    def endpoint(cls):
        return '/sites'

    @classmethod
    def endpoint_single(cls):
        return '/sites/{id}'

    @classmethod
    def entity_class(cls):
        return Site

    @classmethod
    def create(cls, token, site, parameters=None):
        cls.validate_is_entity(site, Site)
        return cls._create(token, site, parameters=parameters)

    @classmethod
    def retrieve_one(cls, token, site_id, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        return cls._retreive_one(token, site_id, parameters=parameters)

    @classmethod
    def retrieve_all(cls, token, parameters=None):
        return cls._retrieve_all(token, parameters=parameters)

    @classmethod
    def update(cls, token, site, parameters=None):
        cls.validate_is_entity(site, Site)
        return cls._update(token, site, parameters=parameters)

    @classmethod
    def delete(cls, token, site_id, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        return cls._delete(token, site_id, parameters=parameters)


__all__ = ['Site', 'Sites']

