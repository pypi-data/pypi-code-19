from __future__ import unicode_literals
from wellaware.base import BaseEntity, JsonProperty


class Role(BaseEntity):
    """
    Roles define permissions and Subjects have Role(s).
    """

    name = JsonProperty('name')


__all__ = ['Role']
