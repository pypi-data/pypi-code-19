from __future__ import unicode_literals

from wellaware.base import BaseEntity, JsonProperty


class Tenant(BaseEntity):
    """
    Represents a Tenant or Sub-Tenant.
    """

    name = JsonProperty('name')
    effective_timestamp = JsonProperty('effectiveTimestamp')
    timezone = JsonProperty('timezone')

__all__ = ['Tenant']
