#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

__all__ = [
    "upsert_many"
]


def upsert_many(col, data):
    """Only used when having "_id" field.

    **中文文档**

    要求 ``data`` 中的每一个 ``document`` 都必须有 ``_id`` 项。这样才能进行
    ``upsert`` 操作。                                                                    
    """
    ready_to_insert = list()
    for doc in data:
        res = col.update({"_id": doc["_id"]}, {"$set": doc}, upsert=False)
        if not res["nModified"]:
            ready_to_insert.append(doc)
    col.insert(ready_to_insert)


if __name__ == "__main__":
    import random
    from pymongo_mate.tests import col

    def test_upsert_many():
        col.remove({})
        data = [
            {"_id": 0},
            {"_id": 1, "v": 0},
        ]
        col.insert(data)

        data = [
            {"_id": 0, "v": 0},
            {"_id": 1, "v": 1},
            {"_id": 2, "v": 2},
        ]
        upsert_many(col, data)
        assert list(col.find()) == [
            {'_id': 0, 'v': 0}, {'_id': 1, 'v': 1}, {'_id': 2, 'v': 2}]

    test_upsert_many()
