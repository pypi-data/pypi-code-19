from __future__ import absolute_import, division, print_function, unicode_literals

import re

from amaascore.error_messages import ERROR_LOOKUP
from amaascore.core.amaas_model import AMaaSModel


class Address(AMaaSModel):

    def __init__(self, line_one, city, country_id, address_primary, line_two=None, region=None, postal_code=None,
                 active=True, version=1, *args, **kwargs):
        self.address_primary = address_primary
        self.line_one = line_one
        self.line_two = line_two
        self.city = city
        self.region = region
        self.postal_code = postal_code
        self.country_id = country_id
        self.active = active
        self.version = version
        super(Address, self).__init__(*args, **kwargs)

    @property
    def country_id(self):
        if hasattr(self, '_country_id'):
            return self._country_id

    @country_id.setter
    def country_id(self, country_id):
        if country_id:
            if len(country_id) != 3:
                raise ValueError(ERROR_LOOKUP.get('country_id_invalid') % country_id)
            self._country_id = country_id


class Email(AMaaSModel):

    def __init__(self, email, email_primary, active=True, version=1, *args, **kwargs):
        self.email_primary = email_primary
        self.email = email
        self.active = active
        self.version = version
        super(Email, self).__init__(*args, **kwargs)

    @property
    def email(self):
        if hasattr(self, '_email'):
            return self._email

    @email.setter
    def email(self, email):
        # Validate email addresses
        if not re.match('[^@]+@[^@]+\.[^@]+', email):
            raise ValueError(ERROR_LOOKUP.get('email_address_invalid') % email)
        self._email = email


class Link(AMaaSModel):

    def __init__(self, linked_party_id, active=True, version=1, *args, **kwargs):
        self.linked_party_id = linked_party_id
        self.active = active
        self.version = version
        super(Link, self).__init__(*args, **kwargs)

class Reference(AMaaSModel):
    
    def __init__(self, reference_value, active=True, *args, **kwargs):
        self.reference_value = reference_value
        self.active = active
        super(Reference, self).__init__(*args, **kwargs)


class Comment(AMaaSModel):
    """
    A free text comment about the party
    """
    @staticmethod
    def party_key():
        return 'comment_type'

    @staticmethod
    def unique():
        return True

    @staticmethod
    def table_name():
        return 'party_comments'

    def __init__(self, comment_value, active=True, *args, **kwargs):
        self.comment_value = comment_value
        self.active = active
        super(Comment, self).__init__(*args, **kwargs)