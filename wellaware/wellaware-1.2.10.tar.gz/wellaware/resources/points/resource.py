from __future__ import unicode_literals

from wellaware.base import BaseResource
from wellaware.resources.sites import Site
from wellaware.resources.assets import Asset
from wellaware.resources.points import Point, PointSettings


class Points(BaseResource):

    @classmethod
    def endpoint(cls):
        return '/sites/{site_id}/assets/{asset_id}/points'

    @classmethod
    def endpoint_single(cls):
        return '/sites/{site_id}/assets/{asset_id}/points/{id}'

    @classmethod
    def entity_class(cls):
        return Point

    @classmethod
    def create(cls, token, site_id, asset_id, point, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        cls.validate_is_entity(point, Point)
        return cls._create(token, point, parameters=parameters, ids={'site_id': site_id, 'asset_id': asset_id})

    @classmethod
    def retrieve_one(cls, token, site_id, asset_id, point_id, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        point_id = cls.get_entity_id(point_id, Point)
        return cls._retreive_one(token, point_id, parameters=parameters, ids={'site_id': site_id, 'asset_id': asset_id})

    @classmethod
    def retrieve_all(cls, token, site_id, asset_id, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        return cls._retrieve_all(token, parameters=parameters, ids={'site_id': site_id, 'asset_id': asset_id})

    @classmethod
    def update(cls, token, site_id, asset_id, point, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        cls.validate_is_entity(point, Point)
        return cls._update(token, point, parameters=parameters, ids={'site_id': site_id, 'asset_id': asset_id})

    @classmethod
    def delete(cls, token, site_id, asset_id, point_id, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        point_id = cls.get_entity_id(point_id, Point)
        return cls._delete(token, point_id, parameters=parameters, ids={'site_id': site_id, 'asset_id': asset_id})


__all__ = ['Point', 'PointSettings', 'Points']
