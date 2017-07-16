# -*- coding: utf-8 -*-

"""
    pyco_mongo
    ~~~~~~~~~~~~~~~~~~~
    which encapsulates MongoMixin by pymongo,
    make use of MongoDB in someway like relative database.
    :copyright: (c) 2017 by Dodoru.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import absolute_import
import os
import time
from bson import ObjectId
from pymongo import (
    MongoClient,
    ASCENDING,
    DESCENDING,
)
from .errors import (
    MongoLocked,
    MongoNotFound,
    MongoKeyFrozen,
    MongoKeyUndefined,
    MongoFieldUnmovable,
)

env = os.environ.get
mongodb_uri = env('MONGODB_URI', "mongodb://localhost:27017")
mongodb_name = env('MONGODB_NAME', "test")
mongodb_col_seq = env('MONGODB_COL_SEQ', "_seq_coll")

client = MongoClient(mongodb_uri)
db = client[mongodb_name]
__seq_col = db[mongodb_col_seq]
__seq_key = 'seq'


def _next_id(collection_name):
    """
    create a unique index of MongoMixin by increase object.id automatically.
    mongo.__seq_cal saves the mappings, which indexes subclass of MongoMixin.
    """
    query = {
        'name': collection_name,
    }
    update = {
        '$inc': {
            __seq_key: 1
        }
    }
    kwargs = {
        'query': query,
        'update': update,
        'upsert': True,
        'new': True,
    }
    obj = __seq_col.find_and_modify(**kwargs)
    new_id = obj.get(__seq_key)
    return new_id


def _reset_id(collection_name, id=1):
    """
    !! danger, use in extreme caution
    """
    query = {
        'name': collection_name,
    }
    update = {
        '$set': {
            __seq_key: id,
        }
    }
    kwargs = {
        'query': query,
        'update': update,
        'upsert': True,
        'new': True,
    }
    obj = __seq_col.find_and_modify(**kwargs)
    new_id = obj.get(__seq_key)
    return new_id


def _coll_cur_id(collection):
    """
    # latest object.id of collection
    """
    query = {'name': collection}
    obj = __seq_col.find_one(query)
    if obj is None:
        raise MongoNotFound(collection)
    seq = obj.get(__seq_key)
    return seq


def _drop(collection_name):
    '''
    # drop collection with clear index-mapping in mongo.__seq_col
    '''
    op1 = db.drop_collection(collection_name)
    op2 = __seq_col.find_one_and_delete(filter={"name": collection_name})
    op1['seq_info'] = op2
    return op1


class MongoMixin(object):
    '''
    # fields ,[(key, type, value),...],
    # looks like MongoMixin.__immutable_fields()

    # frozen_keys, [key1, key2,...] ,
    # values of frozen_keys should not update by cls.update()
    '''
    __fields__ = []
    __frozen_keys__ = []

    @classmethod
    def __immutable_keys(cls):
        #  values of cls.__immutable_keys should not be update by cls.update()
        ks = [
            '_id',
            'id',
        ]
        return ks

    @classmethod
    def __fixed_fields(cls):
        """
        Key Features of MongoMixin.
        !! danger, sub-class of MongoMixin should not rewrite cls.__fixed_fields.
        """
        fs = [
            # (key, type, value)
            # key start with '_' is implicit key, which should be protected.
            ('_id', ObjectId, None),
            ('id', int, -1),
            ('deleted', bool, False),
            ('created_time', int, 0),
            ('updated_time', int, 0),
        ]
        return fs

    @classmethod
    def _valid_fields(cls, fields):
        ks = []
        for f in fields:
            k, t, v = f
            if k in ks:
                msg = 'KEY[{}] is duplicate.'
                raise KeyError(msg)
            else:
                ks.append(k)
            try:
                kv = t(v)
            except:
                msg = 'field of ({},{},{}) is invalid'.format(k, t, v)
                raise ValueError(msg)
        return True

    @classmethod
    def _fields(cls):
        fs = cls.__fixed_fields() + cls.__fields__
        if cls._valid_fields(fs):
            return fs

    @classmethod
    def _frozen_keys(cls):
        ks = cls.__frozen_keys__ + cls.__immutable_keys()
        ks = list(set(ks))
        return ks

    @classmethod
    def keys(cls):
        ks = [x[0] for x in cls._fields()]
        return ks

    @classmethod
    def collection(cls):
        name = cls.__name__
        return db[name]

    def lock(self):
        '''
        # Key Features of MongoMixin. Don't cover it in sub-class.
        '''
        setattr(self, '__locked', True)

    def unlock(self):
        '''
        # Key Features of MongoMixin. Don't cover it in sub-class.
        '''
        if hasattr(self, '__locked'):
            delattr(self, '__locked')

    def is_locked(self):
        '''
        # Key Features of MongoMixin. Don't cover it in sub-class.
        '''
        return hasattr(self, '__locked')

    def __init__(self, **kwargs):
        '''
        :param kwargs: set key-values of fields，
        if value is not found in key-values，use default value predefined in self._fields()
        '''
        for f in self._fields():
            k, t, v = f
            if k in kwargs:
                setattr(self, k, t(kwargs[k]))
            else:
                setattr(self, k, t(v))
        self.lock()

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{0} = {1}'.format(k, v) for k, v in self.__dict__.items())
        return '<{0}: \n  {1}\n>'.format(name, '\n  '.join(properties))

    def __eq__(self, others):
        mf = self.to_dict()
        mt = others.to_dict()
        return mf == mt

    def to_dict(self):
        '''
         In general, self.to_dict() is the same as self.__dict__
        :return: normalize with self.keys()
        '''
        keys = self.keys()
        data = {}
        for k in keys:
            data[k] = getattr(self, k)
        return data

    def json(self):
        """
        :return dictionary which satisfied JSON Object.
        : should not include implicit key set in cls._fields(), eg: _id
        : always include '_type', which indicate the collection name.
        """
        td = self.to_dict()
        d = {k: v for k, v in td.items() if not k.startswith('_')}
        d['_type'] = self.__class__.__name__
        return d

    @classmethod
    def new(cls, **kwargs):
        """
        new instance of MongoMixin and save automatically.
        eg:
        form = {
            'task': '吃饭',
        }
        t = Todo.new(**form, user_id=1)
        """
        m = cls(**kwargs)
        m.id = _next_id(cls.__name__)
        ts = int(time.time())
        m.created_time = ts
        m.updated_time = ts
        m.unlock()
        m.save()
        return m

    @classmethod
    def _new_with_bson(cls, bson):
        """
        retrieve object to instance of MongoMixin.
        """
        m = cls(**bson)
        m.unlock()
        return m

    @classmethod
    def exist(cls):
        return cls.__name__ in db.collection_names()

    @classmethod
    def has(cls, **kwargs):
        return cls.find_one(**kwargs) is not None

    @classmethod
    def count(cls, **kwargs):
        m = cls.collection().count(kwargs)
        return m

    @classmethod
    def paging(cls, skip=0, limit=20, **kwargs):
        '''
        :param skip: int, skips the first `skip` results of this cursor.
        :param limit: int, maximum limit of results.
        :param kwargs:
            __sort_key: key to sort results
            __sort_dir: direction to sort results, ASCENDING==1
        :return: list instance of MongoMixin
        '''
        sort_key = kwargs.pop('__sort_key', 'id')  # key or list
        sort_dir = kwargs.pop('__sort_dir', ASCENDING)
        en = cls.collection().find(kwargs).sort(sort_key, sort_dir)
        ds = en.skip(skip).limit(limit) # Cursor
        ms = [cls._new_with_bson(d) for d in ds]
        return ms

    @classmethod
    def find(cls, **kwargs):
        """
        : query objects, return list of instance.
        : if no object is satisfied, return [].
        """
        sort_key = kwargs.pop('__sort_key', None)
        ds = cls.collection().find(kwargs)
        if sort_key is not None:
            ds = ds.sort(sort_key)
        l = [cls._new_with_bson(d) for d in ds]
        return l

    @classmethod
    def get(cls, id):
        """
        :param id: int, unique, value of key("id") set in cls.__immutable_keys(),
        """
        return cls.find_one(id=id)

    @classmethod
    def find_one(cls, **kwargs):
        """
        :return: If no object is match, return None, else return only one instance.
        """
        bson = cls.collection().find_one(kwargs)
        if bson is not None:
            m = cls._new_with_bson(bson)
            return m

    @classmethod
    def upsert(cls, query, update):
        '''
        :param query: dict, Conditions for querying data， eg {'id':1}
        :param update: dict, Key-Values to update softly， eg {'name':'new_name'}
        :return: if object is existed, then update softly, else new an instance.
        '''
        ms = cls.find_one(**query)
        if ms is None:
            query.update(**update)
            ms = cls.new(**query)
        else:
            ms.update(**update)
        return ms

    def update(self, **kwargs):
        '''
        :param **kwargs: key-values to update keys softly, which not in self._frozen_keys()
        '''
        for k, v in kwargs.items():
            if hasattr(self, k):
                mutable = k not in self._frozen_keys()
                if mutable:
                    setattr(self, k, v)
                else:
                    name = self.__class__.__name__
                    raise MongoKeyFrozen(name, k)
        self.updated_time = int(time.time())
        self.save()

    def save(self):
        '''
        # save unlocked object into collection of db
        # object via cls.new() is unlocked by calling self.unlock() automatically.
        # object via cls.__init__() (or cls()) is locked by calling self.lock().
        !! danger, sub-class of MongoMixin should not rewrite self.save()
        '''
        if self.is_locked():
            raise MongoLocked(self)
        else:
            data = self.__dict__  # 一般和 self.to_dict() 一致
            self.collection().save(data)

    def delete(self):
        '''
        # delete object in logical, which can be recovered.
        '''
        if not self.deleted:
            self.deleted = True
            self.save()

    def recover(self):
        '''
        # recover object which was deleted.
        '''
        if self.deleted:
            self.deleted = False
            self.save()

    def _force_update(self, **kwargs):
        """
        # Update object in force, even value of frozen keys would be updated.
        # Besides, you can't get frozen keys by cls._frozen_keys().
        # self.update() is strongly recommended to use instead of self._force_update()
        !! danger, use in extreme caution
        """
        query = {
            'id': self.id,
        }
        update = {
            '$set': kwargs,
        }
        self.collection().find_and_modify(query=query, update=update)

    def _remove(self):
        """
        # remove object, con't not be recover.
        !! danger, use in extreme caution
        """
        self.collection().remove(self._id)

    @classmethod
    def _rename_field(cls, origin, target):
        """
        # require rewrite code of cls.__fields__ after cls._rename_field()
        !! danger, use in extreme caution
        """
        ms = cls.find()
        for m in ms:
            v = getattr(m, origin)
            delattr(m, origin)
            setattr(m, target, v)
            m.save()

    @classmethod
    def _add_field(cls, key, default_value):
        """
        # require rewrite code of cls.__fields__ before cls._del_field()
        !! danger, use in extreme caution
        """
        if key not in cls.keys():
            raise MongoKeyUndefined(cls.__name__, key)
        ms = cls.find()
        for m in ms:
            setattr(m, key, default_value)
            m.save()

    @classmethod
    def _del_field(cls, key):
        """
        # require rewrite code of cls.__fields__ before cls._del_field()
        !! danger, use in extreme caution
        """
        if key in cls.keys():
            raise MongoFieldUnmovable(cls.__name__, key)
        ms = cls.find()
        for m in ms:
            delattr(m, key)
            m.save()

    @classmethod
    def filter_by_field_values(cls, models, key, values):
        """
        :param instances: models of MongoMixin
        :param key: field key
        :param values: list of values
        :return: [instance1, instance2, ...]
        """
        ds = list(filter(lambda m: (getattr(m, key)) in values, models))
        return ds

    @classmethod
    def group_by_field_values(cls, models, key, values):
        # :param instances: models of MongoMixin
        ds = dict((v, []) for v in values)
        for m in models:
            v = getattr(m, key)
            if v in values:
                ds[v].append(m)
        return ds
