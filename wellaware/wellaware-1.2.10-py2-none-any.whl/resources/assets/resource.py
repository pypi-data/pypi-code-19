from __future__ import unicode_literals

from wellaware.base import BaseResource
from wellaware.resources.sites import Site
from wellaware.resources.assets import Asset


class Assets(BaseResource):

    @classmethod
    def endpoint(cls):
        return '/sites/{site_id}/assets'

    @classmethod
    def endpoint_single(cls):
        return '/sites/{site_id}/assets/{id}'

    @classmethod
    def entity_class(cls):
        return Asset

    @classmethod
    def create(cls, token, site_id, asset, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        cls.validate_is_entity(asset, Asset)
        return cls._create(token, asset, parameters=parameters, ids={'site_id': site_id})

    @classmethod
    def retrieve_one(cls, token, site_id, asset_id, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        return cls._retreive_one(token, asset_id, parameters=parameters, ids={'site_id': site_id})

    @classmethod
    def retrieve_all(cls, token, site_id, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        return cls._retrieve_all(token, parameters=parameters, ids={'site_id': site_id})

    @classmethod
    def update(cls, token, site_id, asset, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        cls.validate_is_entity(asset, Asset)
        return cls._update(token, asset, parameters=parameters, ids={'site_id': site_id})

    @classmethod
    def delete(cls, token, site_id, asset_id, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        return cls._delete(token, asset_id, parameters=parameters, ids={'site_id': site_id})


__all__ = ['Asset', 'Assets']
