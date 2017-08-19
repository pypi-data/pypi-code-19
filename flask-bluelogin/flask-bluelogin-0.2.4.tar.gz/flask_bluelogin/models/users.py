# coding: utf-8
from .base_model_ import Model
from ..util import NotFoundUserError, AlreadyExistUserError, Unauthorized 

class Singleton(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if 'Users' not in cls._instances: #change cls by 'Users'
            cls._instances['Users'] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances['Users']

# create a singleton for python3
#
# class BlueLogin(Blueprint, metaclass=Singleton):
#
# for compatible python2, I use module **six**

import six

@six.add_metaclass(Singleton)
class Users(Model):
    def __init__(self):
        """
        Users
        """
        self._users = {}

    def set_user(self, user):
        if user.id not in self._users:
            raise NotFoundUserError(user.id)
        self._users[user.id] = user
    
    def get_user(self, id):
        try:
            return self._users[id]
        except KeyError as e:
            raise NotFoundUserError(detail=id)
   
    def add_user(self, user):
        if user.id in self._users:
            raise AlreadyExistUserError(user.id)
        self._users[user.id] = user

    def check_password(self, user, password):
        if user.id not in self._users:
            raise NotFoundUserError(user.id)
        return self._users[user.id]._password == password

       
