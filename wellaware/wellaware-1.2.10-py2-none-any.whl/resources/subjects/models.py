from __future__ import unicode_literals
from wellaware.base import BaseEntity, JsonProperty


class Subject(BaseEntity):
    """
    Represents a User.
    """

    username = JsonProperty('username')
    email = JsonProperty('email')
    phone = JsonProperty('phone')
    given_name = JsonProperty('firstName')
    family_name = JsonProperty('lastName')
    password = JsonProperty('password')


__all__ = ['Subject']
