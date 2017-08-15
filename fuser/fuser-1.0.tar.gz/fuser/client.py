from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import relationship, backref

import random
import string
from secrets import token_urlsafe
from flaskapp.extensions import db

import bcrypt
from pga.basemodel import BaseModelMixin
from .user_mixin import UserMixin


class Client(BaseModelMixin, db.Model):
    """A Client is either a browser or an API device. It represents a session but can be 
    thought of as a device, as the cookie or API key wouldn't be reset unless action is 
    taken.
    """

    # Set to false on logged out.
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    client_key = db.Column(db.Text, nullable=False, unique=True)

    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)


    @classmethod
    def create_with_credentials(cls, email, password, client_key):
        from flaskapp.models.user import User
        user_with_email = User.query.filter_by(email=email).first()
        if user_with_email.hashed_pw_matches_plaintext(password):
            authenticated_user = user_with_email

            # What if this user is signing into another account?
            existing_client = Client.query.filter_by(client_key=client_key).filter_by(is_active=True).first()
            if existing_client:
                existing_client.user_id = authenticated_user.id
                returned_client = existing_client
            else:
                new_client = cls(client_key=client_key, user_id=authenticated_user.id)
                returned_client = new_client

            db.session.add(returned_client)
            db.session.commit()
            return returned_client
