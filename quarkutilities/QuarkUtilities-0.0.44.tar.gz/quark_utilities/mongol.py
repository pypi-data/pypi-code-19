from tornado import gen

from . import errors
from bson import ObjectId
from flasky.errors import FlaskyTornError
from pymongo.errors import DuplicateKeyError

__all__ = ["maybe_object_id", "Repository", "create_id"]


class RecordNotExistsError(FlaskyTornError):
    def __init__(self, record_type, record_id):
        super().__init__(status_code=404, err_code="errors.resourceNotFound")
        self.record_type = record_type
        self.record_id = record_id

class IDMismatchError(FlaskyTornError):
    def __init__(self, given_id, data_id):
        super().__init__(message="errors.idMismatchError", err_code="errors.idMismatchError", status_code=400)
        self.given_id = given_id
        self.data_id = data_id

class FlaskyDuplicateKeyError(FlaskyTornError):
    def __init__(self, collection_name, key, pymongo_exc=None):
        super().__init__(status_code=409,
                         message="There is already existing record at <{}> collection"
                                 "with given <{}>key ".format(collection_name, key),
                         err_code="errors.resourceAlreadyExists",
                         reason=pymongo_exc)
        self.collection_name = collection_name
        self.key = key


def raise_resource_not_found_err(collection_name, key):
    raise errors.QError(
        err_code="errors.resourceNotFound",
        status_code=404,
        err_msg="Not found any resource in collection<{}> with given key <{}>".format(collection_name, key),
        context={
            'collection_name': collection_name,
            'key': key
        }
    )


def maybe_object_id(maybe_id):
    if isinstance(maybe_id, ObjectId):
        return maybe_id
    elif not ObjectId.is_valid(maybe_id):
        return maybe_id
    else:
        return ObjectId(maybe_id)

def normalize_ids(where):
    if '_id' in where:
        if type(where['_id']) == dict and "$in" in where['_id']:
            _ids = [
                maybe_object_id(_id)
                for _id in where['_id']['$in']
            ]
            where['_id']['$in'] = _ids
            return where
        elif type(where['_id']) == str:
            where['_id'] = normalize_ids(where['_id'])
            return where
    return where

def create_id():
    return ObjectId()

class Repository(object):

    def __init__(self, collection):
        self.collection = collection

    @property
    def collection_name(self):
        return self.collection.name

    async def query(self, select=None, where=None,
                    sort=None, skip=None, limit=None, return_count=False):
        cur = self.collection.find(where, select)
        count  = await cur.count()

        if skip:
            cur.skip(skip)

        if sort:
            cur.sort(sort)

        if limit:
            cur.limit(limit)

        records = await cur.to_list(length=None)

        if return_count:
            return records, count

        return [record
                for record in records
                if not record.get("is_deleted", False)]

    async def save(self, document, force=False):
        if "_id" not in document:
            document["_id"] = create_id()
        try:
            if force:
                await self.collection.replace_one(
                    {'_id': document['_id']},
                    document,
                    upsert=True
                )
            else:
                await self.collection.save(document)
        except DuplicateKeyError:
            raise errors.QError(
                err_code='errors.duplicateKeyError',
                status_code=409,
                err_msg='There is already existing record in collection<{}>.'.format(self.collection_name),
                context={
                    "collection_name": self.collection_name,
                })

        return document

    async def update(self, _id, data):
        #: Data object should not have id field in it
        #: if it has it should be the same id with given
        #: id
        if "_id" in data:
            if str(_id) != str(data["_id"]):
                raise IDMismatchError(_id, data["_id"])

            data["_id"] = maybe_object_id(data["_id"])

        try:
            await self.collection.replace_one({
                "_id": maybe_object_id(_id)
            }, data)
            return data
        except DuplicateKeyError as e:
            raise FlaskyDuplicateKeyError(
                collection_name=self.collection_name,
                key=data.get("_id"),
                pymongo_exc=e
            )

    async def delete(self, _id):
        record = await self.find(_id=_id)
        if not record:
            raise RecordNotExistsError(self.collection.name, _id)
        await self.collection.remove(record["_id"], record)

    async def delete_one_by(self, where=None):
        record = await self.find_one_by(where=where)
        if not record:
            raise RecordNotExistsError(self.collection.name, where.get("_id", None))

        if "_id" in where:
            where["_id"] = maybe_object_id(where=where)

        await self.collection.deleteOne(where=where)

    async def remove_one_by(self, where=None, raise_exec=True):
        where = normalize_ids(where)

        result = await self.collection.remove(where)

        if result["n"] == 0 and raise_exec:
            raise_resource_not_found_err(
                self.collection,
                where
            )

    async def delete_many_by(self, where=None):
        record = await self.find_one_by(where=where)
        if not record:
            raise RecordNotExistsError(self.collection.name, where.get("_id", None))

        await self.collection.deleteMany(where=where)

    async def find(self, _id=None, raise_exec=True):
        document = await self.collection.find_one({"_id": maybe_object_id(_id)})
        if not document and raise_exec:
            raise RecordNotExistsError(self.collection_name, _id)
        return document

    async def find_one_by(self, where=None, select=None, raise_exec=True):
        if "_id" in where:
            where["_id"] = maybe_object_id(where["_id"])
        document = await self.collection.find_one(where, select)
        if not document and raise_exec:
            raise RecordNotExistsError(self.collection_name, where)
        return document

    async def update_one_by(self, where=None, update=None):
        if '_id' in where:
            where['_id'] = maybe_object_id(where['_id'])

        return await self.collection.update(where, update)









