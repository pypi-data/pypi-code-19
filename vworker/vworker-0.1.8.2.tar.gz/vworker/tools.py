#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from .mongofun import mongofun
from .redisfun import redisfun


def now_time():
    """ 当前UTC时间戳
    """
    return int(time.time() * 1000)


def _get_user_tbl(role='c', is_read_slave=False):
    ''' 用户表
    '''
    collection = mongofun.get_mongo_collection('we_user_db', 'user_{}'.format(role), is_read_slave)
    return collection


def _get_park_info_tbl(is_read_slave=False):
    ''' 园区信息表
    '''
    collection = mongofun.get_mongo_collection('we_user_db', 'park_info', is_read_slave)
    return collection


def get_user_c_data(u_id, item):
    assert isinstance(item, list)
    assert item, 'item cant be empty'
    _redies_key = "new_park_info"

    u_id = int(u_id)
    c_find_filter = {'_id': u_id}
    b_data = {}

    in_b = ['pro_name', 'pro_type', 'com_name', 'park_id', 'b_img']
    in_park = ['park']

    park_refine = list(set(item) & set(in_park))
    b_refine = list(set(item) & set(in_b))

    def foo(index, select_filter):
        attr_name = 'get' if index in item else 'pop'
        if attr_name == 'pop':
            select_filter.append(index)
        return attr_name

    if b_refine or park_refine:
        b_attr_name = foo('pid', item)
    if park_refine:
        park_attr_name = foo('park_id', b_refine)

    userdata = _get_user_tbl('c').find_one(c_find_filter, item)
    if b_refine or park_refine:
        b_attr_obj = getattr(userdata, b_attr_name)
        pid = int(b_attr_obj('pid', 0))
        b_find_filter = {'_id': pid}
        if 'b_img' in b_refine:
            b_refine.remove('b_img')
            b_refine.append('img')
        b_data = _get_user_tbl('b').find_one(b_find_filter, b_refine)
        if not pid:
            park_refine = []
            b_data = {}
        # if userdata.get('park_id', ''):
            # userdata['park_id'] = str(userdata['park_id'])

    if park_refine:
        park_attr_obj = getattr(b_data, park_attr_name)
        park_id = park_attr_obj('park_id', 0)
        park_name = redisfun.redis_conn.hget(_redies_key, park_id)
        if park_name:
            park_name = park_name.decode('utf-8')
        else:
            park_find_filter = {'_id': park_id}
            park_name_dict = _get_park_info_tbl().find_one(park_find_filter, ['name'])
            park_name = park_name_dict.get('name')
            redisfun.redis_conn.hset(_redies_key, park_id, park_name)
        userdata.update({'park': park_name})

    b_img = b_data.pop('img', '')
    if b_img:
        b_data['b_img'] = b_img
    userdata.update(b_data)
    if userdata.get('park_id', ''):
        userdata['park_id'] = str(userdata['park_id'])
    userdata.pop('_id', '')
    return userdata
