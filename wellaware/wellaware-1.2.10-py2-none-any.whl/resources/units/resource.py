from __future__ import unicode_literals

from wellaware.base import BaseResource
from wellaware.resources.units import Unit


class Units(BaseResource):

    @classmethod
    def endpoint(cls):
        return '/units'

    @classmethod
    def endpoint_single(cls):
        return '/units/{id}'

    @classmethod
    def entity_class(cls):
        return Unit

    @classmethod
    def create(cls, token, unit, parameters=None):
        cls.validate_is_entity(unit, Unit)
        return cls._create(token, unit, parameters=parameters)

    @classmethod
    def retrieve_one(cls, token, unit_id, parameters=None):
        unit_id = cls.get_entity_id(unit_id, Unit)
        return cls._retreive_one(token, unit_id, parameters=parameters)

    @classmethod
    def retrieve_all(cls, token, parameters=None):
        return cls._retrieve_all(token, parameters=parameters)

    @classmethod
    def update(cls, token, unit, parameters=None):
        cls.validate_is_entity(unit, Unit)
        return cls._update(token, unit, parameters=parameters)

    @classmethod
    def delete(cls, token, unit_id, parameters=None):
        unit_id = cls.get_entity_id(unit_id, Unit)
        return cls._delete(token, unit_id, parameters=parameters)


__all__ = ['Unit', 'Units']
