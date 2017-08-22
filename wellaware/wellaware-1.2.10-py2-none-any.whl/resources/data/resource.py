from __future__ import unicode_literals
from datetime import datetime

from wellaware._compat import long_, array_types, integer_types
from wellaware.constants import make_headers, datetime_to_ms
from wellaware.base.base_entity import collection_to_json
from wellaware.base.base_resource import BaseResource
from wellaware.resources.common import HttpError
from wellaware.resources.data.data_models import Observation, RollupUpdate, DataOrdering
from wellaware.resources.data.data_errors import DataModificationError, DataRetrieveError, DataSaveError, \
    RollupUpdateError
from wellaware.resources.data.data_responses import DataRetrieveResponse, DataModificationResponse, \
    RollupUpdateResponse, DataSaveResponse
from wellaware.resources.points.models import Point


class Data(BaseResource):

    @classmethod
    def endpoint(cls):
        return '/data'

    @classmethod
    def endpoint_create(cls):
        return cls.endpoint() + '/create'

    @classmethod
    def endpoint_update(cls):
        return cls.endpoint() + '/update'

    @classmethod
    def endpoint_delete(cls):
        return cls.endpoint() + '/delete'

    @classmethod
    def endpoint_replay(cls):
        return cls.endpoint() + '/replay'

    @classmethod
    def endpoint_retrieve(cls):
        return cls.endpoint() + '/retrieve'

    @classmethod
    def endpoint_rollup(cls):
        return cls.endpoint() + '/rollup'

    @classmethod
    def save_new_data(cls, token, observations, parameters=None):
        cls.validate_is_entity(observations, array_types)
        for observation in observations:
            cls.validate_is_entity(observation, Observation)
        response = cls.REST_CLIENT.post(
            cls.get_base_uri(cls.endpoint_create()),
            data=collection_to_json(observations),
            headers=make_headers(token),
            params=parameters
        )
        response = cls.REST_CLIENT.handle_response(response)
        errors = response.json().get('errors', [])
        e = []
        for error in errors:
            http_error = HttpError.from_dict(error)
            observation = Observation.from_dict(error.get('observation', {}))
            e.append(DataSaveError(
                observation=observation, error_code=http_error.error_code, error_message=http_error.error_message
            ))
        return DataSaveResponse(errors=e)

    @classmethod
    def update_data(cls, token, observations, parameters=None):
        cls.validate_is_entity(observations, array_types)
        for observation in observations:
            cls.validate_is_entity(observation, Observation)
        response = cls.REST_CLIENT.post(
            cls.get_base_uri(cls.endpoint_update()),
            data=collection_to_json(observations),
            headers=make_headers(token),
            params=parameters
        )
        response = cls.REST_CLIENT.handle_response(response)
        errors = response.json().get('errors', [])
        e = []
        for error in errors:
            http_error = HttpError.from_dict(error)
            observation = Observation.from_dict(error.get('observation', {}))
            e.append(DataModificationError(
                observation=observation, error_code=http_error.error_code, error_message=http_error.error_message
            ))
        return DataModificationResponse(errors=e)

    @classmethod
    def delete_data(cls, token, observations, parameters=None):
        cls.validate_is_entity(observations, array_types)
        for observation in observations:
            cls.validate_is_entity(observation, Observation)
        response = cls.REST_CLIENT.post(
            cls.get_base_uri(cls.endpoint_delete()),
            data=collection_to_json(observations),
            headers=make_headers(token),
            params=parameters
        )
        response = cls.REST_CLIENT.handle_response(response)
        errors = response.json().get('errors', [])
        e = []
        for error in errors:
            http_error = HttpError.from_dict(error)
            observation = Observation.from_dict(error.get('observation', {}))
            e.append(DataModificationError(
                observation=observation, error_code=http_error.error_code, error_message=http_error.error_message
            ))
        return DataModificationResponse(errors=e)

    @classmethod
    def replay_data(cls, token, point_ids, start=None, end=None, limit=None, offset=None, parameters=None):
        cls.validate_is_entity(point_ids, array_types)
        if parameters is None:
            parameters = {}
        ids = []
        for point_id in point_ids:
            ids.append(cls.get_entity_id(point_id, Point))

        if start is not None:
            if isinstance(start, integer_types) or isinstance(start, datetime):
                parameters['start'] = datetime_to_ms(start)

        if end is not None:
            if isinstance(end, integer_types) or isinstance(end, datetime):
                parameters['end'] = datetime_to_ms(end)

        if limit is not None and isinstance(limit, integer_types) and limit > 0:
            parameters['limit'] = limit

        if offset is not None and isinstance(offset, integer_types) and offset > 0:
            parameters['offset'] = offset

        response = cls.REST_CLIENT.post(
            cls.get_base_uri(cls.endpoint_replay()),
            json={'pointIds': ids},
            headers=make_headers(token),
            params=parameters
        )

        response = cls.REST_CLIENT.handle_response(response)
        response = response.json()

        errors = []
        for e in response.get('errors', []):
            errors.append(DataRetrieveError.from_dict(e))

        return DataRetrieveResponse(errors=errors, observations={})

    @classmethod
    def retrieve_data(cls, token, point_ids, start=None, end=None, limit=None, offset=None, order=None, parameters=None):
        cls.validate_is_entity(point_ids, array_types)
        if parameters is None:
            parameters = {}
        ids = []
        for point_id in point_ids:
            ids.append(cls.get_entity_id(point_id, Point))

        if start is not None:
            if isinstance(start, integer_types) or isinstance(start, datetime):
                parameters['start'] = datetime_to_ms(start)

        if end is not None:
            if isinstance(end, integer_types) or isinstance(end, datetime):
                parameters['end'] = datetime_to_ms(end)

        if limit is not None and isinstance(limit, integer_types) and limit > 0:
            parameters['limit'] = limit

        if offset is not None and isinstance(offset, integer_types) and offset > 0:
            parameters['offset'] = offset

        if order in [DataOrdering.DESCENDING, DataOrdering.ASCENDING]:
            parameters['order'] = order

        response = cls.REST_CLIENT.post(
            cls.get_base_uri(cls.endpoint_retrieve()),
            json={'pointIds': ids},
            headers=make_headers(token),
            params=parameters
        )

        response = cls.REST_CLIENT.handle_response(response)
        response = response.json()
        errors = []
        for e in response.get('errors', []):
            errors.append(DataRetrieveError.from_dict(e))

        observations = {}
        for point_id, obs in response.get('observations', {}).items():
            if point_id not in observations:
                observations[long_(point_id)] = []
            for o in obs:
                observation = Observation.from_dict(o)
                observation.point_id = long_(point_id)
                observations[long_(point_id)].append(observation)

        return DataRetrieveResponse(observations=observations, errors=errors)

    @classmethod
    def rollup_date(cls, token, rollup_updates, parameters=None):
        cls.validate_is_entity(rollup_updates, array_types)
        for rollup_update in rollup_updates:
            cls.validate_is_entity(rollup_update, RollupUpdate)
        response = cls.REST_CLIENT.post(
            cls.get_base_uri(cls.endpoint_rollup()),
            data=collection_to_json(rollup_updates),
            headers=make_headers(token),
            params=parameters
        )
        response = cls.REST_CLIENT.handle_response(response)
        response = response.json()

        errors = []
        for e in response.get('errors', []):
            http_error = HttpError.from_dict(e)
            rollup_update = RollupUpdate.from_dict(e.get('rollupUpdate', {}))
            errors.append(RollupUpdateError(
                rollup=rollup_update, error_code=http_error.error_code, error_message=http_error.error_message
            ))

        rollups = {}
        for point_id, ru in response.get('rollupUpdates', {}).items():
            if point_id not in rollups:
                rollups[long_(point_id)] = []
            for r in ru:
                rollup = RollupUpdate.from_dict(r)
                rollup.point_id = long_(point_id)
                rollups[long_(point_id)].append(rollup)

        return RollupUpdateResponse(rollup_updates=rollups, errors=errors)

__all__ = ['Data']
