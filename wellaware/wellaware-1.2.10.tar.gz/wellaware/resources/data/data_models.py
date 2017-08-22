from __future__ import unicode_literals

from wellaware._compat import add_metaclass
from wellaware.base import BaseAbstractEntity, BaseEntityMetaType, JsonProperty


@add_metaclass(BaseEntityMetaType)
class Observation(BaseAbstractEntity):
    """
    Represents an Observation for a Point Stream.

    This is a time-value object with some additional meta-data.
    """

    point_id = JsonProperty('pointId')
    timestamp = JsonProperty('timestamp')
    received = JsonProperty('receivedTimestamp')
    value = JsonProperty('value')
    email = JsonProperty('email')


@add_metaclass(BaseEntityMetaType)
class RollupUpdate(BaseAbstractEntity):
    """
    A Rollup Update request.
    """
    point_id = JsonProperty('pointId')
    timestamp = JsonProperty('timestamp')


@add_metaclass(BaseEntityMetaType)
class DataRetrieveRequest(BaseAbstractEntity):
    """
    Represents a request for data.
    """
    start_timestamp = JsonProperty('start')
    end_timestamp = JsonProperty('end')
    order = JsonProperty('order')
    limit = JsonProperty('limit')
    point_ids = JsonProperty('pointIds', klass=list)


class DataOrdering(object):

    DESCENDING = '-timestamp'
    ASCENDING = '+timestamp'


__all__ = ['Observation', 'RollupUpdate', 'DataRetrieveRequest', 'DataOrdering']
