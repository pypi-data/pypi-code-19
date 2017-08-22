from __future__ import unicode_literals

from wellaware.base import BaseEntity, JsonProperty


class Site(BaseEntity):
    """
    Represents a Site containing Assets.
    """

    name = JsonProperty('name')
    latitude = JsonProperty('latitude')
    longitude = JsonProperty('longitude')
    timezone = JsonProperty('timezone')


__all__ = ['Site', 'Sites']
