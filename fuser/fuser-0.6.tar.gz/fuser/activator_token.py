from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import relationship, backref
from flask import current_app

import random

from secrets import token_urlsafe
from flaskapp.extensions import db

import bcrypt
from pga.basemodel import BaseModelMixin

import hashlib, binascii
from sqlalchemy import Column, Integer, String, Enum
from datetime import datetime

class ActivatorToken(db.Model, BaseModelMixin):
    """
        This is a device for linking a user to an email address.

        An activator is an EXPIRING* 

        * The expiring nature of the Activator is the whole reason it's still secure.
        It's safe to assume that the user wants this. 

        These can either be used for (1) Password Resets (2) First time setup 

        They can be sent via SMS and Email

        TODO: could factor this out into different subclasses using enums. Could allow
        SMS to be validated this way too.
    """

    function = db.Column(db.Text, nullable=False, unique=False)
    activator_code = db.Column(db.Text, nullable=False, unique=True)

    # Set to false after used or a new one created
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)

    def __init__(self, function, user_id):
        self.function = function
        self.user_id = user_id
        self.activator_code = token_urlsafe(32)

    def is_expired(self):
        return (datetime.utcnow() - self.timestamp).days > 2

    @classmethod
    def activator_token_for_user(cls, user, function):
        exisiting_valid_tokens = cls.query.filter_by(user_id=user.id)\
                                           .filter_by(is_active=True)\
                                           .all()
        if exisiting_valid_tokens:
            for token in exisiting_valid_tokens:
                token.is_active = False

            db.session.add_all(exisiting_valid_tokens)
            db.session.commit()

        new_token = cls(function=function, user_id=user.id)
        db.session.add(new_token)
        db.session.commit()
        return new_token
