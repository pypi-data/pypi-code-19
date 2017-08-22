from __future__ import unicode_literals

from wellaware._compat import add_metaclass, long_
from wellaware.base import BaseAbstractEntity, BaseEntityMetaType, JsonProperty
from data_models import RollupUpdate, Observation
from data_errors import DataSaveError, DataRetrieveError, DataModificationError


@add_metaclass(BaseEntityMetaType)
class RollupUpdateResponse(BaseAbstractEntity):
    """
    Represents a Rollup Update Response.
    """

    rollup_updates = JsonProperty('rollupUpdates', klass=list, list_klass=RollupUpdate)
    errors = JsonProperty('errors')


@add_metaclass(BaseEntityMetaType)
class DataSaveResponse(BaseAbstractEntity):
    """
    Represents a Data Create Response.
    """

    errors = JsonProperty('errors', klass=list, list_klass=DataSaveError)


@add_metaclass(BaseEntityMetaType)
class DataRetrieveResponse(BaseAbstractEntity):
    """
    Represents a Data Retrieve Response.
    """

    observations = JsonProperty('observations', klass=dict)
    errors = JsonProperty('errors', klass=list, list_klass=DataRetrieveError)


@add_metaclass(BaseEntityMetaType)
class DataModificationResponse(BaseAbstractEntity):
    """
    Represents a Data Update Response.
    """

    errors = JsonProperty('errors', klass=list, list_klass=DataModificationError)


__all__ = ['DataSaveResponse', 'DataModificationResponse', 'DataRetrieveResponse', 'RollupUpdateResponse']


