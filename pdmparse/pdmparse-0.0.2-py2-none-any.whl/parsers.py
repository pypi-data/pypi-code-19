# encoding: utf-8

'''
Created on 2014-7-19
@author: hshl.ltd
'''

# http://django.readthedocs.org/en/latest/releases/1.7.html#standalone-scripts
# https://docs.python.org/2/library/xml.etree.elementtree.html


from __future__ import unicode_literals

import os

from xml.etree import ElementTree as ET

from .table import Table, Column, Reference, ReferenceJoin


def get_pdm_root(pdm_path):
    """获取pdm文件的root根元素"""
    if (not os.path.exists(pdm_path)):
        raise IOError('pdm文件%s不存在' % pdm_path)

    with open(pdm_path, 'r') as f:
        pdm_str = f.read().decode('UTF-8')

    """由于pdm xml中包含有命名空间，所以第一步读取后替换掉命名空间然后通过ET进行解析
    ,命名空间字符 'o:','c:','a:',为什么要替换掉命名空间，主要原因是使用ET的register_namespace后解析失败
    <Model xmlns:a="attribute" xmlns:c="collection" xmlns:o="object">
    <o:RootObject Id="o1">
    <c:Children>
    <o:Model Id="o2">
    ........
    </o:RootObject>
    """
    xmlns = ('o:', 'c:', 'a:')
    for re in xmlns:
        pdm_str = pdm_str.replace(re, '')
    root = ET.fromstring(pdm_str)
    return root


def read(pdm_path):
    root = get_pdm_root(pdm_path)

    # 获取pdm文件中的表集合及表的相关属性
    ele_tables = [
        t for t in root.iter('Table') if t.attrib.get('Id', None) is not None]
    tables = [Table(t.attrib.get('Id'), t.findtext('Name'), t.findtext('Code'),
                    t.findtext('CreationDate'), t.findtext('Creator')) for t in ele_tables]

    # 获取pdm文件中的表与表之间的引用关系，包括join、子表、父表
    ele_references = [
        ref for ref in root.iter('Reference') if ref.attrib.get('Id', None) is not None]
    references = []
    for ref in ele_references:
        ref_id = ref.attrib.get('Id')
        ptable_id = ref.find('ParentTable/Table').attrib.get('Ref')
        ctable_id = ref.find('ChildTable/Table').attrib.get('Ref')
        parent_keyid = ref.find('ParentKey/Key').attrib.get('Ref')
        ele_joins = ref.findall('Joins/ReferenceJoin')
        joins = []
        for ele_join in ele_joins:
            join_id = ele_join.attrib.get('Id')
            ptable_column_id = ele_join.find(
                'Object1/Column').attrib.get('Ref')
            ctable_column_id = ele_join.find(
                'Object2/Column').attrib.get('Ref')
            joins.append(
                ReferenceJoin(join_id, ptable_column_id, ctable_column_id))
        references.append(
            Reference(ref_id, ptable_id, ctable_id, parent_keyid, joins))

    for ele_table in ele_tables:
        table = [
            t for t in tables if t.obj_id == ele_table.attrib.get('Id')][0]

        # 获取表的Keys，Key与列之间的引用关系
        keys = []
        for key in ele_table.iterfind('Keys/Key'):
            key_id = key.attrib.get('Id')
            key_col_ref = [
                col.attrib.get('Ref') for col in key.iterfind('Key.Columns/Column')]
            for ref in key_col_ref:
                keys.append({'key_id': key_id, 'key_col_ref': ref})

        # 主键对Key的引用关系
        ele_pk_key = ele_table.find('PrimaryKey/Key')
        if ele_pk_key is None:
            pk_key_ref = None
        else:
            pk_key_ref = ele_pk_key.attrib.get('Ref')

        # 在这里假定Keys不是主键(PK)就是唯一键(AK)
        pks = []
        aks = []
        for key in keys:
            if key['key_id'] == pk_key_ref:
                pks.append(key['key_col_ref'])
            else:
                aks.append(key['key_col_ref'])

        # 获取当前表包含的列
        ele_columns = [e for e in ele_table.find(
            'Columns') if e.attrib.get('Id', None) is not None]
        columns = []
        for ele_column in ele_columns:
            column_id = ele_column.attrib.get('Id')
            column_name = ele_column.findtext('Name')
            column_code = ele_column.findtext('Code')
            column_data_type = ele_column.findtext('DataType')
            column_length = ele_column.findtext('Length')
            column_precision = ele_column.findtext('Precision')
            is_pk = column_id in pks
            is_ak = column_id in aks
            is_fk = len([ref for ref in references if ref.ctable_id ==
                         table.obj_id and column_id in ref.ctable_column_ids]) > 0
            is_mandatory = ele_column.findtext('Mandatory') is not None
            is_identity = ele_column.findtext('Identity') is not None

            column = Column(column_id, column_name, column_code, column_data_type,
                            column_length, column_precision, is_pk, is_ak, is_fk,
                            is_mandatory, is_identity)
            columns.append(column)
        table.columns = columns

    # 完善FnReference对象的属性，因为在前面只是获得了表和列的id，通过这个步骤将引用（FnReference）的父子表、
    # join的键对应关系表实例化为FnTable，FnColumn对象
    for ref in references:
        for table in tables:
            if table.obj_id == ref.ptable_id:
                ref.ptable = table
            if table.obj_id == ref.ctable_id:
                ref.ctable = table

        for join in ref.joins:
            join.ptable_column = [
                cloumn for cloumn in ref.ptable.columns if cloumn.obj_id == join.ptable_column_id][0]
            join.ctable_column = [
                cloumn for cloumn in ref.ctable.columns if cloumn.obj_id == join.ctable_column_id][0]

    # 完善Table的父引用和子引用属性
    for table in tables:
        table.parent_refs = [
            ref for ref in references if ref.ctable_id == table.obj_id]
        table.child_refs = [
            ref for ref in references if ref.ptable_id == table.obj_id]
    return tables
