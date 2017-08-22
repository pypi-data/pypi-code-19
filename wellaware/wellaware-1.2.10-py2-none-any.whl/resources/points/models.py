from __future__ import unicode_literals

from wellaware.base import BaseEntity, JsonProperty


class PointSettings(object):
    """
    Common Point Settings
    """

    class DataTypes(object):
        DOUBLE = 'double'
        FLOAT = 'float'
        INTEGER = 'integer'
        LONG = 'long'
        SHORT = 'short'
        BYTE = 'byte'
        BOOLEAN = 'boolean'
        STRING = 'string'
        MAP = 'map'

    class PointTypes(object):
        LATITUDE = 'LATITUDE'
        LONGITUDE = 'LONGITUDE'
        CONTRACT_HOUR = 'CONTRACT_HOUR'
        NOTE = 'NOTE'

    class RollupTypes(object):
        LATEST = 'latest'
        AVERAGE = 'average'


class Point(BaseEntity):
    """
    Represents a Point which represents and observation stream or parameter.
    """

    name = JsonProperty('name')
    point_type = JsonProperty('pointType')
    data_type = JsonProperty('dataType')
    rollup_type = JsonProperty('rollupType')
    expected_period_ms = JsonProperty('expectedPeriodMs')
    timezone = JsonProperty('timezone')
    unit = JsonProperty('unit')
    color = JsonProperty('color')
    is_parameter = JsonProperty('isParameter')
    is_process_variable = JsonProperty('isProcessVar')
    is_hidden = JsonProperty('isHidden')
    is_graphed_by_default = JsonProperty('isGraphedByDefault')
    is_shown_in_summary = JsonProperty('isShownInSummary')
    is_accumulable = JsonProperty('isAccumulable')
    is_automated = JsonProperty('isAutomated')


__all__ = ['Point', 'PointSettings']
