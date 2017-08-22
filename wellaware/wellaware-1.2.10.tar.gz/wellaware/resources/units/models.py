from __future__ import unicode_literals

from wellaware.base import BaseEntity, JsonProperty


class Unit(BaseEntity):
    """
    Represents a Unit which defines the Point units.
    """

    name = JsonProperty('name')
    abbreviation = JsonProperty('abbreviation')


__all__ = ['Unit']
