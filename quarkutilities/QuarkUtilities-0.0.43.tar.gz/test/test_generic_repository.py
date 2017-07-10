from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from tornado.testing import AsyncTestCase, gen_test
from tornado.platform.asyncio import AsyncIOMainLoop

from quark_utilities.db import GenericRepository, create_id, GRDuplicateKeyError, GRResourceNotFoundError, normalize_ids


class TestGenericRepository(AsyncTestCase):

    def setUp(self):
        super(TestGenericRepository, self).setUp()
        self.client = AsyncIOMotorClient("localhost")
        self.repo = GenericRepository(self.client.test.test_collection)

    def get_new_ioloop(self):
        return AsyncIOMainLoop()

    @gen_test
    async def test_save_method(self):
        repo = GenericRepository(self.client.test.test_collection)
        saved = await repo.save({
            "email": "test@test.com.tr"
        })

        self.assertIsNotNone(saved['_id'])

        founded = await repo.find_one_by_id(saved['_id'])

        self.assertEquals(founded['_id'], saved['_id'])

    @gen_test
    async def test_save_method_should_raise_duplicate_key_error(self):
        _id = create_id()

        await self.repo.save({
            "_id": _id,
            'key': 'val'
        })

        try:
            await self.repo.save({
                '_id': _id,
                'key': 'val'
            })
        except GRDuplicateKeyError as e:
            self.assertEquals(e.err_code, "errors.documentConflict")
            return

        self.assertFalse(True, "exception did not raised")

    @gen_test
    async def test_find_one_by_id_should_raise_exc_if_doc_not_found(self):
        try:
            await self.repo.find_one_by_id(_id="test")
        except GRResourceNotFoundError as e:
            self.assertEquals(e.err_code, "errors.notFoundError")
            return

        self.assertFalse(True, "Exception did not raised...")


    @gen_test
    async def test_query_should_return_all_items(self):
        doc_1 = {
            '_id': create_id(),
            'test': 'val'
        }

        doc_2 = {
            '_id': create_id(),
            'test': 'val2'
        }

        await self.repo._collection.drop()

        await self.repo._collection.save(doc_1)
        await self.repo._collection.save(doc_2)


        docs, count = await self.repo.query()

        self.assertEquals(count, 2)
        self.assertEquals(len(docs), 2)

    @gen_test
    async def test_update_one(self):
        doc = {
            '_id': create_id()
        }

        await self.repo.save(doc)

        doc.update({
            "test": "val"
        })
        await self.repo.replace_one(doc)

        founded = await self.repo.find_one_by_id(doc['_id'])
        self.assertEquals(founded['test'], doc['test'])

    @gen_test
    async def test_delete_one_by(self):
        doc = {
            '_id': create_id()
        }

        await self.repo.save(doc)

        await self.repo.delete_one_by_id(_id=doc['_id'])

        founded = self.repo.find_one_by_id(_id=doc['_id'], raise_exec=False)

        self.assertIsNotNone(founded)

    @gen_test
    async def test_normalize_ids(self):
        where = normalize_ids({
            "_id": {
                '$in': [str(create_id()), str(create_id())]
            }
        })

        for _id in where['_id']['$in']:
            self.assertEquals(type(_id), ObjectId)