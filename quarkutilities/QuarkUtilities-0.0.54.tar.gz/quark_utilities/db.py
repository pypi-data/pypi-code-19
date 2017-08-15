from bson import ObjectId
from pymongo.errors import DuplicateKeyError


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


class GRError(Exception):
    def __init__(self, err_code=None, message=None, context=None):
        self.err_code = err_code
        self.message = message
        self.context = context


class GRDuplicateKeyError(GRError):

    def __init__(self, collection_name, context):
        super(GRDuplicateKeyError, self).__init__(
            err_code="errors.documentConflict",
            message="There is already existing document in collection<{}> with given key"
                .format(collection_name),
            context=context
        )


class GRResourceNotFoundError(GRError):
    def __init__(self, collection_name, context):
        super(GRResourceNotFoundError, self).__init__(
            err_code="errors.notFoundError",
            message="Resource not found in collection<{}> with given key.".format(collection_name),
            context=context
        )


class GenericRepository(object):

    def __init__(self, collection):
        self._collection = collection
        self._max_document_limit = 500

    @property
    def name(self):
        return self._collection.name

    async def find_one_by_id(self, _id, raise_exec=True):
        return await self.find_one_by(
            where={
                "_id": maybe_object_id(_id)
            },
            raise_exec=raise_exec
        )

    async def find_one_by(self, where=None, select=None, raise_exec=True):
        document = await self._collection.find_one(
            where,
            select
        )

        if not document and raise_exec:
            raise GRResourceNotFoundError(self.name, context={
                "where": where,
                "select": select
            })

        return document

    async def save(self, document):
        if "_id" not in document:
            document['_id'] = create_id()
        try:
            await self._collection.insert_one(document)
        except DuplicateKeyError as e:
            raise GRDuplicateKeyError(
                self.name,
                context={
                    'document': document
                }
            ) from e

        return document

    async def replace_one(self, document, raise_exec=True):
        if not '_id' in document:
            raise GRError(
                err_code="errors.badDocument",
                message="Can't update document without _id field.",
                context={
                    "document": document
                }
            )

        key = {
            "_id": maybe_object_id(document['_id'])
        }

        result = await self._collection.replace_one(key, document)

        if result.modified_count == 0 and raise_exec:
            raise GRResourceNotFoundError(self.name,
                context={
                    "key": key
                }
            )

        return document

    async def delete_one_by_id(self, _id):
        _id = maybe_object_id(_id)

        key = {
            "_id": _id
        }

        result = await self._collection.delete_one(key)

        if result.deleted_count == 0:
            raise GRResourceNotFoundError(
                self.name,
                context={
                    'key': key
                }
            )

    async def query(self, where=None, select=None, skip=None,
                    limit=None, sort=None):

        where = normalize_ids(where) if where else {}

        cur = self._collection.find(
            where,
            select
        )

        total_document_count = await cur.count()

        if limit: cur.limit(int(limit))
        if skip: cur.skip(int(skip))
        if sort: cur.sort(sort)

        documents = await cur.to_list(length=None)

        return documents, total_document_count

