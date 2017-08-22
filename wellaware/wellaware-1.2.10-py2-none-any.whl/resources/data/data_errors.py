from __future__ import unicode_literals

from wellaware.base import JsonProperty
from wellaware.resources.common import HttpError
from data_models import Observation, RollupUpdate


class RollupUpdateError(HttpError):
    """
    Rollup update error.
    """

    rollup = JsonProperty('rollupUpdate', klass=RollupUpdate)


class DataSaveError(HttpError):
    """
    A Data Create error.
    """

    observation = JsonProperty('observation', klass=Observation)


class DataRetrieveError(HttpError):
    """
    A Data Retrieve Error message.
    """

    point_id = JsonProperty('pointId')


class DataModificationError(HttpError):
    """
    A Data Modification Error.
    """

    observation = JsonProperty('observation', klass=Observation)


__all__ = ['RollupUpdateError', 'DataSaveError', 'DataRetrieveError', 'DataModificationError']