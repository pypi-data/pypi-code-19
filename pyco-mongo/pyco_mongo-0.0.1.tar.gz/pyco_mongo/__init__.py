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
    用来给 mongo 的数据模型生成一个 自增的数字 id, 默认放在 seqcoll 表里
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
    慎用
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
    # 某数据集合当前的id
    query = {'name': collection}
    obj = __seq_col.find_one(query)
    if obj is None:
        raise MongoNotFound(collection)
    seq = obj.get(__seq_key)
    return seq


def _drop(collection_name):
    # 删除某数据集合，慎用
    op1 = db.drop_collection(collection_name)
    op2 = __seq_col.find_one_and_delete(filter={"name": collection_name})
    op1['seq_info'] = op2
    return op1


class MongoMixin(object):
    __fields__ = []
    __frozen_keys__ = []

    # fields 的样式[(字段名, 类型, 值),...]
    # 格式和 __immutable_fields 一致
    # frozen_keys [字段名, 字段名,...] 不能通过 update 软更新

    @classmethod
    def __immutable_keys(cls):
        ks = [
            '_id',
            'id',
        ]
        return ks

    @classmethod
    def __fixed_fields(cls):
        fs = [
            # (字段名, 类型, 值)
            # 以 _开头的字段名，为隐式键，不会包括在json()中
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
        setattr(self, '__locked', True)

    def unlock(self):
        if hasattr(self, '__locked'):
            delattr(self, '__locked')

    def is_locked(self):
        return hasattr(self, '__locked')

    def __init__(self, **kwargs):
        '''
        :param kwargs: 设置 fields 的字段值，如果没有，使用默认值
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

    def to_dict(self):
        # 作用相似 __dict__
        keys = self.keys()
        data = {}
        for k in keys:
            data[k] = getattr(self, k)
        return data

    def json(self):
        """
        json 函数返回 model 的 json 字典,
        1. 默认不包括隐式字段的数据, 比如_id
        2. 默认有_type ，默认值为类名
        """
        td = self.to_dict()
        d = {k: v for k, v in td.items() if not k.startswith('_')}
        d['_type'] = self.__class__.__name__
        return d

    def __eq__(self, others):
        mf = self.to_dict()
        mt = others.to_dict()
        return mf == mt

    @classmethod
    def new(cls, **kwargs):
        """
        new 是给外部使用的函数， 用于创建并保存新数据
        例如
        form = {
            'task': '吃饭',
        }
        t = Todo.new(form, user_id=1)
        new 是自动 save 的, 所以使用后不需要 save
        """
        # 创建一个空对象
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
        这是给内部函数使用的函数
        从 mongo 数据中恢复一个 model
        你不用关心
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
        sort_key = kwargs.pop('__sort_key', 'id')  # key or list
        sort_dir = kwargs.pop('__sort_dir', ASCENDING)  # 升序 1， 降序 -1
        en = cls.collection().find(kwargs).sort(sort_key, sort_dir)
        ds = en.skip(skip).limit(limit) # Cursor
        ms = [cls._new_with_bson(d) for d in ds]
        return ms

    @classmethod
    def find(cls, **kwargs):
        """
        mongo 数据查询
        例如
        ts = Todo.find(user_id=1)
        返回的是 list
        找不到就是 []
        """
        # kwargs.setdefault('deleted', False)  # 默认只查找没删除的数据
        sort_key = kwargs.pop('__sort_key', None)
        ds = cls.collection().find(kwargs)
        if sort_key is not None:
            ds = ds.sort(sort_key)
        l = [cls._new_with_bson(d) for d in ds]
        return l

    @classmethod
    def get(cls, id):
        return cls.find_one(id=id)

    @classmethod
    def find_one(cls, **kwargs):
        """
        和 find 一样， 但是只返回第一个元素
        找不到就返回 None
        """
        bson = cls.collection().find_one(kwargs)
        if bson is not None:
            m = cls._new_with_bson(bson)
            return m

    @classmethod
    def upsert(cls, query, update, hard=False):
        '''
        这个东西略微复杂 你可以忽略
        :param query:  查询数据的条件， eg {'id':1}
        :param update: 更新数据的键值， eg {'name':'new_name'}
        :param hard:  默认为False, 如果设置为 True, 可更新 __fields__ 尚未预定义好的属性
        :return: 查询数据，如果没有数据，就插入数据； 如果有数据，就更新数据；
        '''
        ms = cls.find_one(**query)
        if ms is None:
            query.update(**update)
            ms = cls.new(**query)
        else:
            ms.update(**update, hard=hard)
        return ms

    def update(self, **kwargs):
        '''
        :param form: 更新数据，form 是一个表单
        :param hard: 默认为 False, 如果设置为 True, 可更新 __frozen_keys__ 的值
        '''
        hard = kwargs.pop('hard', False)
        for k, v in kwargs.items():
            if hasattr(self, k):
                mutable = k not in self._frozen_keys()
                if hard or mutable:
                    setattr(self, k, v)
                else:
                    name = self.__class__.__name__
                    raise MongoKeyFrozen(name, k)
        self.updated_time = int(time.time())
        self.save()

    def save(self):
        '''
        保存数据
        '''
        if self.is_locked():
            raise MongoLocked(self)
        else:
            data = self.__dict__  # 一般和 self.to_dict() 一致
            self.collection().save(data)

    def _update(self, **kwargs):
        query = {
            'id': self.id,
        }
        update = {
            '$set': kwargs,
        }
        self.collection().find_and_modify(query=query, update=update)

    def delete(self):
        '''
        删除数据，这里的数据是一种逻辑删除
        '''
        if not self.deleted:
            self.deleted = True
            self.save()

    def recover(self):
        if self.deleted:
            self.deleted = False
            self.save()

    def _remove(self):
        '''
        :return: 硬删除，慎用
        '''
        self.collection().remove(self._id)

    @classmethod
    def _rename_field(cls, origin, target):
        """
        清洗数据用的函数
        例如 User._rename_field('is_hidden', 'deleted')
        把 is_hidden 字段重命名为 deleted 字段
        """
        ms = cls.find()
        for m in ms:
            v = getattr(m, origin)
            delattr(m, origin)
            setattr(m, target, v)
            m.save()

    @classmethod
    def _add_field(cls, key, default_value):
        ''' require update cls.__fields__ before cls._add_field() '''
        if key not in cls.keys():
            raise MongoKeyUndefined(cls.__name__, key)
        ms = cls.find()
        for m in ms:
            setattr(m, key, default_value)
            m.save()

    @classmethod
    def _del_field(cls, key):
        if key in cls.keys():
            raise MongoFieldUnmovable(cls.__name__, key)
        ms = cls.find()
        for m in ms:
            delattr(m, key)
            m.save()
