from __future__ import unicode_literals

from wellaware._compat import add_metaclass
from wellaware.base import BaseAbstractEntity, BaseEntityMetaType, BaseEntity, JsonProperty


class ControlPoint(BaseEntity):
    """
    Represents a ControlPoint.

    Something which can be changed remotely.
    """

    name = JsonProperty('name')
    tag = JsonProperty('tag')
    site_id = JsonProperty('siteId')
    asset_id = JsonProperty('assetId')
    point_id = JsonProperty('pointId')
    data_type = JsonProperty('dataType')
    enabled = JsonProperty('enabled')
    hidden = JsonProperty('hidden')
    timeout = JsonProperty('timeout')
    locked_by_subject_id = JsonProperty('lockedBySubjectId')
    locked_by_subject_username = JsonProperty('lockedBySubjectUsername')
    locked_at = JsonProperty('lockedAt')
    lock_expires_at = JsonProperty('lockExpiresAt')
    latest_value = JsonProperty('latestValue')
    latest_value_timestamp = JsonProperty('latestValueTimestamp')
    parent_control_point_name = JsonProperty('parentControlPointName')
    parent_bit_mask = JsonProperty('parentBitMask')
    lower_numeric_bound = JsonProperty('lowerNumericBound')
    upper_numeric_bound = JsonProperty('upperNumericBound')
    string_length_bound = JsonProperty('stringLengthBound')
    string_enumeration_bound = JsonProperty('stringEnumerationBound', klass=list)
    value_enumeration_bound = JsonProperty('valueEnumerationBound', klass=list)
    string_value_enumeration = JsonProperty('stringValueEnumeration', klass=dict)


@add_metaclass(BaseEntityMetaType)
class SetPointRequest(BaseAbstractEntity):
    """
    A Set Point Request.
    """

    value = JsonProperty('value')
    previous_value = JsonProperty('previousValue')


__all__ = ['ControlPoint', 'SetPointRequest']
