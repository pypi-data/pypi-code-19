from __future__ import unicode_literals

from wellaware.base import BaseEntity, JsonProperty


class ControlRuleType(object):

    VALUE_MATCH = "valuematch"
    TRIGGER = "trigger"
    STRING_MATCH = "stringmatch"


class ControlRuleTargetDirectionMatch(object):

    MATCH = True
    OPPOSITE = False


class ControlRule(BaseEntity):
    """
    Represents a ControlPoint.

    Something which can be changed remotely.
    """

    name = JsonProperty('name')
    enabled = JsonProperty('enabled')
    order = JsonProperty('order')
    site_id = JsonProperty('siteId')
    asset_id = JsonProperty('assetId')
    point_id = JsonProperty('pointId')
    control_point_id = JsonProperty('controlPointId')
    rule_type = JsonProperty('type')
    rule_value = JsonProperty('ruleValue')
    rule_direction_match = JsonProperty('ruleDirectionMatch')
    rule_string_value = JsonProperty('ruleStringValue')
    target_control_point_name = JsonProperty('targetControlPointName')


__all__ = ['ControlRule', 'ControlRuleType', 'ControlRuleTargetDirectionMatch']
