#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
pymongo query convenence method.
"""

try:
    from ..pkg.sixmini import string_types
except:
    from pymongo_mate.pkg.sixmini import string_types


__all__ = [
    "select_all",
    "select_field",
    "select_distinct_field",
    "random_sample",
]


def select_all(col):
    """Select all document from collection.
    """
    return list(col.find())


def _preprocess_field_or_fields(field_or_fields):
    if isinstance(field_or_fields, string_types):
        field_or_fields = [field_or_fields, ]
    elif isinstance(field_or_fields, (tuple, list)):
        pass
    return field_or_fields


def select_field(col, field_or_fields, filters=None):
    """Select single or multiple fields.

    :params field_or_fields: str or list of str
    :returns headers: headers
    :return data: list of row

    **中文文档**

    - 在选择单列时, 返回的是 str, list.
    - 在选择多列时, 返回的是 str list, list of list.

    返回单列或多列的数据。
    """
    fields = _preprocess_field_or_fields(field_or_fields)

    if filters is None:
        filters = dict()

    wanted = {field: True for field in fields}

    if len(fields) == 1:
        header = fields[0]
        data = [doc.get(header) for doc in col.find(filters, wanted)]
        return header, data
    else:
        headers = list(fields)
        data = [[doc.get(header) for header in headers]
                for doc in col.find(filters, wanted)]
        return headers, data


def select_distinct_field(col, field_or_fields, filters=None):
    """Select distinct value or combination of values of 
    single or multiple fields.

    :params fields: str or list of str.
    :return data: list of list.

    **中文文档**

    选择多列中出现过的所有可能的排列组合。
    """
    fields = _preprocess_field_or_fields(field_or_fields)

    if filters is None:
        filters = dict()

    if len(fields) == 1:
        key = fields[0]
        data = list(col.find(filters).distinct(key))
        return data
    else:
        pipeline = [
            {
                "$match": filters
            },
            {
                "$group": {
                    "_id": {key: "$" + key for key in fields},
                },
            },
        ]
        data = list()
        for doc in col.aggregate(pipeline):
            # doc = {"_id": {"a": 0, "b": 0}} ...
            data.append([doc["_id"][key] for key in fields])
        return data


def random_sample(col, n=5, filters=None):
    """Randomly select n document from query result set. If no query specified,
    then from entire collection.

    **中文文档**

    从collection中随机选择 ``n`` 个样本。
    """
    pipeline = list()
    if filters is not None:
        pipeline.append({"$match": filters})
    pipeline.append({"$sample": {"size": n}})
    return list(col.aggregate(pipeline))
