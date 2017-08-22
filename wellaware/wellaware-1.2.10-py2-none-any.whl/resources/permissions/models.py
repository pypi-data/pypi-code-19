from __future__ import unicode_literals

from wellaware.base import BaseEntity, JsonProperty


class Permission(BaseEntity):
    """
    Represents a Permission which defines Course and Fine-Grained permisisons for resources.
    """

    name = JsonProperty('name')
    resources = JsonProperty('resources')
    actions = JsonProperty('actions')
    ids = JsonProperty('ids')


__all__ = ['Permission']
