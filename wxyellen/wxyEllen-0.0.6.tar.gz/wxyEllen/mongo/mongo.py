import pymongo
import gridfs
from bson.objectid import ObjectId


class MongoB(object):
    """base class of mongo db"""
    def __init__(self, co, db):
        self.co = co.Me()
        self.db = self.co[db]

    def O2S(self, doc):
        if doc:
            doc.update({'_id': str(doc.get('_id'))})
        return doc

    def S2O(self, _id):
        return {'_id': ObjectId(_id)}


class MongoC(object):
    """client of mongo db"""
    def __init__(self, uri):
        self.co = pymongo.MongoClient(uri)

    def Me(self):
        return self.co


class MongoD(MongoB):
    """ document op of mongodb"""
    def __init__(self, co, db, cl):
        super(MongoD,self).__init__(co, db)
        self.cl = self.db[cl]

    def Add(self, doc):
        self.cl.insert_one(doc)
        return self.O2S(doc)

    def All(self, qry):
        return list(map(lambda i: self.O2S(i), self.cl.find(qry)))

    def Get(self, _id):
        return self.O2S(self.cl.find_one(self.S2O(_id)))

    def Set(self, _id, doc):
        return self.O2S(self.cl.find_one_and_update(
                            self.S2O(_id),
                            {'$set': doc},
                            return_document=pymongo.ReturnDocument.AFTER))

    def Del(self, _id):
        return self.O2S(self.cl.find_one_and_delete(self.S2O(_id)))


class MongoF(MongoB):
    """ gridfs op of mongodb"""
    def __init__(self, co, db, cl):
        super(MongoF, self).__init__(co, db)
        self.cl = gridfs.GridFS(self.db, cl)

    def Add(self, doc):
        return {'_id': str(self.cl.put(doc))}

    def Get(self, _id):
        return self.cl.get(ObjectId(_id))

    def Del(self, _id):
        return self.cl.delete(ObjectId(_id))
