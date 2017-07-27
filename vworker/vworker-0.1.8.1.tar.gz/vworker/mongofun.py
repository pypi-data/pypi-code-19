#!/usr/bin/python
# -*- coding: UTF-8 -*-

from pymongo import ReadPreference
from pymongo import MongoClient
from bson.objectid import ObjectId
from .config import config

READ_SLAVE = ReadPreference.SECONDARY_PREFERRED
READ_PRIMARY = ReadPreference.PRIMARY


class Mongofun(object):

    def __init__(self, mongodb_host):
        self.mongodb_host = mongodb_host
        self.ObjectId = ObjectId

    def get_mongo_collection(self, db_name, collection_name, is_read_slave=False):
        """
        获取collection
        """
        mongodb_client = MongoClient(self.mongodb_host)
        kw = {'name': collection_name}
        if is_read_slave:
            kw['read_preference'] = READ_SLAVE
        return mongodb_client.get_database(db_name).get_collection(**kw)


    @classmethod
    def dict_objid_to_str(cls, data):
        ''' obj(_id) => str(_id)
        '''
        try:
            data['_id'] = str(data['_id'])
        except Exception:
            pass
        return data

    @classmethod
    def mongo_find(cls, collection, last_id=None, page_size=None,
                sort_filter=None, sorttype=-1, page_type='page_down',
                self=0, find_filter={}, select_filter={}):
        """ mgdb find 翻页大礼包
        [必选]
        :collection: collection对象
        [可选]
        :last_id: 翻页用标记位 _id
        :page_size: 每页条目个数
        :sort_filter: 排序选项
        :sorttype: 1:正序 -1:倒序
        :page_type: page_down:下一页 page_up:上一页
        :find_filter: 查找过滤器字典 mongodb格式 例:{'s_id':123456}
        :select_filter: 选择过滤器字典 mongodb格式 例:{'or_id':1,'or_num':1}
        :self: 包括last_id自己

        """
        rollover = 0
        if sorttype == -1:  # -1:倒序, 1:正序
            page_type = '$gt' if page_type == 'page_up' else '$lt'
            sorttype = 1 if page_type == '$gt' else -1
            rollover = 1 if page_type == '$gt' else 0
        else:
            page_type = '$lt' if page_type == 'page_up' else '$gt'
        if self:  # 包括自己
            page_type = ''.join([page_type, 'e'])

        '''
        $gt |   1           |  正序下一页
            v   12          v
                123
                1234
                12345
            ^   123456      ^
        $lt |   1234567     |  倒序下一页
        '''

        if last_id and len(last_id) == 24 and isinstance(last_id, basestring):
            find_filter.update({'_id': {page_type: ObjectId(last_id)}})

        args = [find_filter]
        if select_filter:
            args.append(select_filter)
        cursor = collection().find(*args)
        if not sort_filter is None:
            cursor = cursor.sort(sort_filter, sorttype)
        if not page_size is None:
            cursor = cursor.limit(page_size)
        if rollover:
            # cursor = [x for x in cursor][::-1]
            cursor = list(cursor)
            # 反转列表
            cursor.reverse()
        return cursor

    @classmethod
    def mongo_find_pagenum(cls, collection, skip_num=0, page_size=10,
                        sort_filter='c', sorttype=-1,
                        find_filter={}, select_filter={}):
        """ mgdb find 页码翻页大礼包
        [必选]
        :collection: collection对象
        [可选]
        :skip: 跳过数目
        :page_size: 每页条目个数 默认:10条
        :sort_filter: 排序选项 默认根据 c 排序
        :sorttype: 1:正序 -1:倒序
        :find_filter: 查找过滤器字典 mongodb格式 例:{'s_id':123456}
        :select_filter: 选择过滤器字典 mongodb格式 例:{'or_id':1,'or_num':1}
        """
        total = collection().find(find_filter).count()
        if select_filter:
            cursor = collection().find(find_filter, select_filter).sort(
                sort_filter, sorttype).skip(skip_num).limit(page_size)
        else:
            cursor = collection().find(find_filter).sort(
                sort_filter, sorttype).skip(skip_num).limit(page_size)
        return cursor, total

mongofun = Mongofun(config['mongodb'])
