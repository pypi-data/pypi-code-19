from __future__ import unicode_literals

from wellaware._compat import add_metaclass, long_
from wellaware.base import BaseAbstractEntity, BaseEntity, BaseEntityMetaType, JsonProperty


@add_metaclass(BaseEntityMetaType)
class SiteGroupSummary(BaseAbstractEntity):
    asset_type = JsonProperty('assetType')
    point_type = JsonProperty('pointType')
    aggregation_type = JsonProperty('aggregationType')
    label = JsonProperty('label')
    unit = JsonProperty('unit')


@add_metaclass(BaseEntityMetaType)
class SiteGroupViewConfig(BaseAbstractEntity):
    summaries = JsonProperty('summaries', klass=SiteGroupSummary)


@add_metaclass(BaseEntityMetaType)
class SiteGroupNotificationSetting(BaseAbstractEntity):
    notify_sms = JsonProperty('notifySms')
    notify_email = JsonProperty('notifyEmail')


@add_metaclass(BaseEntityMetaType)
class SiteGroupNotificationResponse(BaseAbstractEntity):
    settings = JsonProperty('settings', klass=dict, dict_key_klass=long_, dict_value_klass=SiteGroupNotificationSetting)


class SiteGroup(BaseEntity):
    """
    Represents a SiteGroup which contains Sites.
    """

    name = JsonProperty('name')


__all__ = ['SiteGroup']
