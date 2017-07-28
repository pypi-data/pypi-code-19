from ..mongo import Mongo

class MongoController(Mongo):
    def __init__(self,host, port, db):
        super(MongoController,self).__init__(host, port, db)
        self.collection = "Controller"

    def insert_job(self,job):
        selected_collection = self.connection[self.collection]
        selected_collection.insert_one(job)
