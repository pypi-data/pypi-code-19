# encoding: utf-8

'''
Created on 2014-7-19
@author: hshl.ltd
'''

from __future__ import unicode_literals


class Table(object):

    def __init__(self, obj_id, name, code, creator, creationdate):
        self.obj_id = obj_id
        self.name = name
        self.code = code
        self.creator = creator
        self.creationdate = creationdate

        self._columns = None
        self._parent_refs = None
        self._child_refs = None

    def __repr__(self, *args, **kwargs):
        return "<Table>(name='%s', code='%s', creator='%s', creationdate='%s')" % (
            self.name, self.code, self.creator, self.creationdate)

    @property
    def columns(self):
        """列"""
        return self._columns

    @columns.setter
    def columns(self, value):
        self._columns = value

    @property
    def parent_refs(self):
        """父引用"""
        return self._parent_refs

    @parent_refs.setter
    def parent_refs(self, value):
        self._parent_refs = value

    @property
    def child_refs(self):
        """子引用"""
        return self._child_refs

    @child_refs.setter
    def child_refs(self, value):
        self._child_refs = value

    @property
    def ref_columns(self):
        """被引用的列"""
        codes = []
        cols = []
        for ref in self.child_refs:
            for join in ref.joins:
                if join.ptable_column.code not in codes:
                    codes.append(join.ptable_column.code)
                    cols.append(join.ptable_column)
        return cols

    @property
    def keys(self):
        """主键列表"""
        if self.columns is None:
            return None
        return [col for col in self.columns if col.is_pk]

    @property
    def ak_columns(self):
        """唯一键列表"""
        if self.columns:
            return None
        return [col for col in self.columns if col.is_ak]

    @property
    def identity_columns(self):
        """自增长的列"""
        if self.columns:
            return None
        return [col for col in self.columns if col.is_identity]


class Column(object):

    def __init__(self, obj_id, name, code, data_type, length, precision,
                 is_pk, is_ak, is_fk, is_mandatory, is_identity):
        self.obj_id = obj_id
        self.name = name
        self.code = code
        self.data_type = data_type
        self.length = length
        self.precision = precision
        self.is_pk = is_pk
        self.is_ak = is_ak
        self.is_fk = is_fk
        self.is_mandatory = is_mandatory
        self.is_identity = is_identity

    def __repr__(self, *args, **kwargs):
        return ("<Column>(obj_id='%s', name='%s', code='%s', data_type='%s', length='%s',"
                "precision='%s', is_pk='%s', is_ak='%s', is_fk='%s', is_mandatory='%s', "
                "is_identity='%s')") % (
            self.obj_id, self.name, self.code, self.data_type, self.length, self.precision,
            self.is_pk, self.is_ak, self.is_fk, self.is_mandatory, self.is_identity)


class Reference(object):

    def __init__(self, obj_id, ptable_id, ctable_id, parent_keyid, joins):
        self.obj_id = obj_id
        self.ptable_id = ptable_id
        self.ctable_id = ctable_id
        self.parent_keyid = parent_keyid
        self.joins = joins

        self._ptable = None
        self._ctable = None
        self._ptable_column_ids = None
        self._ctable_column_ids = None

    def __repr__(self, *args, **kwargs):
        return ("<Reference>(obj_id='%s', ptable_id='%s', ctable_id='%s', "
                "parent_keyid='%s', joins='%s')") % (
            self.obj_id, self.ptable_id, self.ctable_id, self.parent_keyid, self.joins)

    @property
    def ptable(self):
        """父表"""
        return self._ptable

    @ptable.setter
    def ptable(self, value):
        self._ptable = value

    @property
    def ctable(self):
        """子表"""
        return self._ctable

    @ctable.setter
    def ctable(self, value):
        self._ctable = value

    @property
    def ptable_column_ids(self):
        if self._ptable_column_ids is None:
            self._ptable_column_ids = [
                join.ptable_column_id for join in self.joins]
        return self._ptable_column_ids

    @property
    def ctable_column_ids(self):
        if self._ctable_column_ids is None:
            self._ctable_column_ids = [
                join.ctable_column_id for join in self.joins]
        return self._ctable_column_ids


class ReferenceJoin(object):

    def __init__(self, obj_id, ptable_column_id, ctable_column_id):
        self.obj_id = obj_id
        self.ptable_column_id = ptable_column_id
        self.ctable_column_id = ctable_column_id

        self._ptable_column = None
        self._ctable_column = None

    def __repr__(self, *args, **kwargs):
        return "<ReferenceJoin>(obj_id='%s', ptable_column_id='%s', ctable_column_id='%s')" % (
            self.obj_id, self.ptable_column_id, self.ctable_column_id)

    @property
    def ptable_column(self):
        return self._ptable_column

    @ptable_column.setter
    def ptable_column(self, value):
        self._ptable_column = value

    @property
    def ctable_column(self):
        return self._ctable_column

    @ctable_column.setter
    def ctable_column(self, value):
        self._ctable_column = value
