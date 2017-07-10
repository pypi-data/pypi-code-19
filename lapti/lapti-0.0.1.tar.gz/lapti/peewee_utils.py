# -*- coding: utf-8 -*-

import base64
import json
import simplejson
import pickle

import peewee
from playhouse.fields import CompressedField
from playhouse.flask_utils import FlaskDB

__all__ = ['PatchedDB', 'JSONField', 'CompressedJSONField', 'BinaryCompressedField']


class PatchedDB(FlaskDB):
    # Патч для для peewee
    def connect_db(self):
        try:
            is_closed = self.database.is_closed()
        except AttributeError:
            # Это неинициализированный Proxy
            is_closed = True
        if is_closed:
            self.database.connect()


class SafeEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super(SafeEncoder, self).default(self, obj)
        except TypeError:
            try:
                return {'__pickled_object__': base64.b64encode(pickle.dumps(obj)).decode()}
            except:
                return '__unencoded_object__'


def pickle_hook(dct):
    if '__pickled_object__' in dct:
        try:
            return pickle.loads(base64.b64decode(dct['__pickled_object__']))
        except:
            return '__unencoded_object__'
    return dct


class JSONField(peewee.TextField):
    db_field = 'text'

    def get_db_field(self):
        db = self.get_database()
        if 'json' in getattr(db, 'field_overrides', {}):
            return 'json'
        return self.db_field

    def python_value(self, value):
        value = value or '{}'
        if isinstance(value, str):
            return json.loads(value, encoding='utf-8', object_hook=pickle_hook)
        return value

    def db_value(self, value):
        return json.dumps(value, cls=SafeEncoder)


class CompressedJSONField(CompressedField):
    def db_value(self, value):
        if value is not None:
            return super(CompressedJSONField, self).db_value(json.dumps(value, cls=SafeEncoder))

    def python_value(self, value):
        if value is not None:
            # simplejson лучше обрабатывает большие обьемы данных
            return simplejson.loads(
                super(CompressedJSONField, self).python_value(value), 'utf-8', object_hook=pickle_hook
            )


class BinaryCompressedField(CompressedField):
    def db_value(self, value):
        return self.compress(value, self.compression_level)

    def python_value(self, value):
        if value is not None:
            return self.decompress(value)
