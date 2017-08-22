from __future__ import unicode_literals

from wellaware.constants import make_headers
from wellaware.base import BaseResource
from wellaware.resources.sites.resource import Site
from wellaware.resources.assets.resource import Asset
from wellaware.resources.points.resource import Point
from wellaware.resources.controlpoints import ControlPoint, SetPointRequest
from wellaware.resources.controlaudits import ControlAudit


class ControlPoints(BaseResource):

    @classmethod
    def endpoint(cls):
        return '/sites/{site_id}/assets/{asset_id}/points/{point_id}/controlpoints'

    @classmethod
    def endpoint_single(cls):
        return '/sites/{site_id}/assets/{asset_id}/points/{point_id}/controlpoints/{id}'

    @classmethod
    def endpoint_on_demand_read(cls):
        return '/sites/{site_id}/assets/{asset_id}/points/{point_id}/controlpoints/{id}/read'

    @classmethod
    def endpoint_set_point_change(cls):
        return '/sites/{site_id}/assets/{asset_id}/points/{point_id}/controlpoints/{id}/set'

    @classmethod
    def entity_class(cls):
        return ControlPoint

    @classmethod
    def create(cls, token, site_id, asset_id, point_id, control_point, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        point_id = cls.get_entity_id(point_id, Point)
        cls.validate_is_entity(control_point, ControlPoint)
        return cls._create(token, control_point, parameters=parameters,
                           ids={'site_id': site_id, 'asset_id': asset_id, 'point_id': point_id})

    @classmethod
    def retrieve_one(cls, token, site_id, asset_id, point_id, control_point_id, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        point_id = cls.get_entity_id(point_id, Point)
        control_point_id = cls.get_entity_id(control_point_id, ControlPoint)
        return cls._retreive_one(token, control_point_id, parameters=parameters,
                                 ids={'site_id': site_id, 'asset_id': asset_id, 'point_id': point_id})

    @classmethod
    def retrieve_all(cls, token, site_id, asset_id, point_id, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        point_id = cls.get_entity_id(point_id, Point)
        return cls._retrieve_all(token, parameters=parameters,
                                 ids={'site_id': site_id, 'asset_id': asset_id, 'point_id': point_id})

    @classmethod
    def update(cls, token, site_id, asset_id, point_id, control_point, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        point_id = cls.get_entity_id(point_id, Point)
        cls.validate_is_entity(control_point, ControlPoint)
        return cls._update(token, control_point, parameters=parameters,
                           ids={'site_id': site_id, 'asset_id': asset_id, 'point_id': point_id})

    @classmethod
    def delete(cls, token, site_id, asset_id, point_id, control_point_id, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        point_id = cls.get_entity_id(point_id, Point)
        control_point_id = cls.get_entity_id(control_point_id, ControlPoint)
        return cls._delete(token, control_point_id, parameters=parameters,
                           ids={'site_id': site_id, 'asset_id': asset_id, 'point_id': point_id})

    @classmethod
    def on_demand_read_options(cls, token, site_id, asset_id, point_id, control_point_id, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        point_id = cls.get_entity_id(point_id, Point)
        control_point_id = cls.get_entity_id(control_point_id, ControlPoint)
        response = cls.REST_CLIENT.options(
            cls.get_base_uri(cls.endpoint_on_demand_read(),
                             site_id=site_id, asset_id=asset_id, point_id=point_id, id=control_point_id),
            headers=make_headers(token),
            params=parameters
        )
        cls.REST_CLIENT.handle_response(response)
        return response.headers.get('Allow', 'OPTIONS').split(',')

    @classmethod
    def on_demand_set_options(cls, token, site_id, asset_id, point_id, control_point_id, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        point_id = cls.get_entity_id(point_id, Point)
        control_point_id = cls.get_entity_id(control_point_id, ControlPoint)
        response = cls.REST_CLIENT.options(
            cls.get_base_uri(cls.endpoint_set_point_change(),
                             site_id=site_id, asset_id=asset_id, point_id=point_id, id=control_point_id),
            headers=make_headers(token),
            params=parameters
        )
        cls.REST_CLIENT.handle_response(response)
        return response.headers.get('Allow', 'OPTIONS').split(',')

    @classmethod
    def on_demand_read(cls, token, site_id, asset_id, point_id, control_point_id, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        point_id = cls.get_entity_id(point_id, Point)
        control_point_id = cls.get_entity_id(control_point_id, ControlPoint)
        response = cls.REST_CLIENT.post(
            cls.get_base_uri(cls.endpoint_on_demand_read(),
                             site_id=site_id, asset_id=asset_id, point_id=point_id, id=control_point_id),
            headers=make_headers(token),
            params=parameters
        )
        cls.REST_CLIENT.handle_response(response)
        return ControlAudit.from_dict(response.json())

    @classmethod
    def on_demand_set(cls, token, site_id, asset_id, point_id, control_point_id, set_point_request, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        point_id = cls.get_entity_id(point_id, Point)
        control_point_id = cls.get_entity_id(control_point_id, ControlPoint)
        cls.validate_is_entity(set_point_request, SetPointRequest)
        response = cls.REST_CLIENT.post(
            cls.get_base_uri(cls.endpoint_set_point_change(),
                            site_id=site_id, asset_id=asset_id, point_id=point_id, id=control_point_id),
            json=set_point_request.get_json_data(),
            headers=make_headers(token),
            params=parameters
        )
        cls.REST_CLIENT.handle_response(response)
        return ControlAudit.from_dict(response.json())


__all__ = ['ControlPoint', 'ControlPoints']
