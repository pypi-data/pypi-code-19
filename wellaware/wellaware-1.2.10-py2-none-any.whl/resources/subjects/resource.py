from __future__ import unicode_literals

from wellaware.base import BaseResource
from wellaware.resources.subjects import Subject


class Subjects(BaseResource):

    @classmethod
    def endpoint(cls):
        return '/subjects'

    @classmethod
    def endpoint_single(cls):
        return '/subjects/{id}'

    @classmethod
    def entity_class(cls):
        return Subject

    @classmethod
    def create(cls, token, subject, parameters=None):
        cls.validate_is_entity(subject, Subject)
        return cls._create(token, subject, parameters=parameters)

    @classmethod
    def retrieve_one(cls, token, subject_id, parameters=None):
        subject_id = cls.get_entity_id(subject_id, Subject)
        return cls._retreive_one(token, subject_id, parameters=parameters)

    @classmethod
    def retrieve_all(cls, token, parameters=None):
        return cls._retrieve_all(token, parameters=parameters)

    @classmethod
    def me(cls, token, parameters=None):
        return cls._retreive_one(token, None, ids={'id': 'me'}, parameters=parameters)

    @classmethod
    def update(cls, token, subject, parameters=None):
        cls.validate_is_entity(subject, Subject)
        return cls._update(token, subject, parameters=parameters)

    @classmethod
    def delete(cls, token, subject_id, parameters=None):
        subject_id = cls.get_entity_id(subject_id, Subject)
        return cls._delete(token, subject_id, parameters=parameters)


__all__ = ['Subject', 'Subjects']
