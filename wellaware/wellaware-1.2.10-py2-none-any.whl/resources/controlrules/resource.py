from __future__ import unicode_literals

from wellaware.base import BaseResource
from wellaware.resources.sites.resource import Site
from wellaware.resources.assets.resource import Asset
from wellaware.resources.points.resource import Point
from wellaware.resources.controlpoints import ControlPoint
from wellaware.resources.controlrules import ControlRule, ControlRuleType, ControlRuleTargetDirectionMatch


class ControlRules(BaseResource):

    @classmethod
    def endpoint(cls):
        return '/sites/{site_id}/assets/{asset_id}/points/{point_id}/controlpoints/{control_point_id}/rules'

    @classmethod
    def endpoint_single(cls):
        return '/sites/{site_id}/assets/{asset_id}/points/{point_id}/controlpoints/{control_point_id}/rules/{id}'

    @classmethod
    def entity_class(cls):
        return ControlRule

    @classmethod
    def create(cls, token, site_id, asset_id, point_id, control_point_id, control_rule, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        point_id = cls.get_entity_id(point_id, Point)
        control_point_id = cls.get_entity_id(control_point_id, ControlPoint)
        cls.validate_is_entity(control_rule, ControlRule)
        return cls._create(token, control_rule, parameters=parameters,
                           ids={'site_id': site_id, 'asset_id': asset_id, 'point_id': point_id,
                                'control_point_id': control_point_id})

    @classmethod
    def retrieve_one(cls, token, site_id, asset_id, point_id, control_point_id, control_rule_id, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        point_id = cls.get_entity_id(point_id, Point)
        control_point_id = cls.get_entity_id(control_point_id, ControlPoint)
        control_rule_id = cls.get_entity_id(control_rule_id, ControlRule)
        return cls._retreive_one(token, control_rule_id, parameters=parameters,
                                 ids={'site_id': site_id, 'asset_id': asset_id, 'point_id': point_id,
                                      'control_point_id': control_point_id})

    @classmethod
    def retrieve_all(cls, token, site_id, asset_id, point_id, control_point_id, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        point_id = cls.get_entity_id(point_id, Point)
        control_point_id = cls.get_entity_id(control_point_id, ControlPoint)
        return cls._retrieve_all(token, parameters=parameters,
                                 ids={'site_id': site_id, 'asset_id': asset_id, 'point_id': point_id,
                                      'control_point_id': control_point_id})

    @classmethod
    def update(cls, token, site_id, asset_id, point_id, control_point_id, control_rule, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        point_id = cls.get_entity_id(point_id, Point)
        control_point_id = cls.get_entity_id(control_point_id, ControlPoint)
        cls.validate_is_entity(control_rule, ControlRule)
        return cls._update(token, control_rule, parameters=parameters,
                           ids={'site_id': site_id, 'asset_id': asset_id, 'point_id': point_id,
                                'control_point_id': control_point_id})

    @classmethod
    def delete(cls, token, site_id, asset_id, point_id, control_point_id, control_rule_id, parameters=None):
        site_id = cls.get_entity_id(site_id, Site)
        asset_id = cls.get_entity_id(asset_id, Asset)
        point_id = cls.get_entity_id(point_id, Point)
        control_point_id = cls.get_entity_id(control_point_id, ControlPoint)
        control_rule_id = cls.get_entity_id(control_rule_id, ControlRule)
        return cls._delete(token, control_rule_id, parameters=parameters,
                           ids={'site_id': site_id, 'asset_id': asset_id, 'point_id': point_id,
                                'control_point_id': control_point_id})


__all__ = ['ControlRule', 'ControlRules', 'ControlRuleType', 'ControlRuleTargetDirectionMatch']
