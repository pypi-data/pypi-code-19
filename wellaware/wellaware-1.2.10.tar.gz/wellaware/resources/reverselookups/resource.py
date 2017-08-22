from __future__ import unicode_literals

from wellaware._compat import long_
from wellaware.constants import make_headers
from wellaware.base.base_resource import BaseResource
from wellaware.resources.common import HttpError
from wellaware.resources.reverselookups.models import ReverseLookup, MultiReverseLookup


class ReverseLookups(BaseResource):

    @classmethod
    def endpoint(cls):
        return '/reverselookup/'

    @classmethod
    def endpoint_single(cls):
        return '/reverselookup/'

    @classmethod
    def entity_class(cls):
        return ReverseLookup

    @classmethod
    def lookup(cls, token, entity_id, expand=False, parameters=None):
        if parameters is None:
            parameters = {}
        parameters['id'] = cls.get_entity_id(entity_id, ReverseLookup)
        parameters['expand'] = expand

        response = cls.REST_CLIENT.get(
            cls.get_base_uri(cls.endpoint_single()),
            headers=make_headers(token),
            params=parameters
        )
        response = cls.REST_CLIENT.handle_response(response)

        return ReverseLookup.from_dict(response.json())

    @classmethod
    def multi_lookup(cls, token, entity_ids, expand=False, parameters=None):
        if parameters is None:
            parameters = {}
        parameters['expand'] = expand
        ids = []
        for entity_id in entity_ids:
            ids.append(cls.get_entity_id(entity_id, ReverseLookup))

        response = cls.REST_CLIENT.post(
            cls.get_base_uri(cls.endpoint()),
            json=ids,
            headers=make_headers(token),
            params=parameters
        )
        response = cls.REST_CLIENT.handle_response(response)

        # handle response
        r = response.json()
        lookups = []
        for lookup in r.get('lookups', []):
            lookups.append(ReverseLookup.from_dict(lookup))
        errors = {}
        for entity_id, error in r.get('errorIds', {}).items():
            errors[long_(entity_id)] = HttpError.from_dict(error)
        return MultiReverseLookup(lookups=lookups, error_ids=errors)


__all__ = ['ReverseLookups']
