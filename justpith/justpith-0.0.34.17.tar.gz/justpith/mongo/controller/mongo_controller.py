from ..mongo import Mongo

class MongoController(Mongo):
    def __init__(self,host, port, db):
        super(MongoController,self).__init__(host, port, db)
        self.collection = "Controller"

    def insert_job(self,job):
        selected_collection = self.connection[self.collection]
        selected_collection.insert_one(job)

    def insert_model_into_job(self, job_id, model_id, type):
        selected_collection = self.connection[self.collection]
        if type == "text":
            result = selected_collection.update_one({"_id":job_id},{"$set":{"id_text": str(model_id)}})
        elif type == "matrix":
            result = selected_collection.update_one({"_id":job_id}, {"$set": {"id_matrix": str(model_id)}})

    def get_job(self, job_id):
        selected_collection = self.connection[self.collection]
        result = selected_collection.find_one({"_id": job_id} )
        return result