from __future__ import unicode_literals

from wellaware.base import BaseEntity, JsonProperty


class Asset(BaseEntity):
    """
    Represents an Asset containing Points.
    """

    name = JsonProperty('name')
    asset_type = JsonProperty('assetType')
    timezone = JsonProperty('timezone')


__all__ = ['Asset']
