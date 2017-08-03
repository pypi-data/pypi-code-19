from ..mongo import Mongo

class MongoTeacher(Mongo):
    def __init__(self,host, port, db):
        super(MongoTeacher,self).__init__(host, port, db)


    def insert_vote(self, collection, news_id, user_id, vote):
        #controllare se esiste un doc per la news
        selected_collection = self.connection[collection]
        result = selected_collection.find_one({"_id":news_id})
        tot = 1
        if result:
            #aggiorna il voto per l'utente
            #aggiungi +1 a tot
            tot = result["tot"] + 1
            updated = selected_collection.update_one({'_id':int(news_id)}, {"$set":{"tot":int(tot), "register." + str(user_id): int(vote)}}, upsert=False)
        else:
            #inserisci
            tmp = {
                "_id": int(news_id),
                "tot": tot,
                "register":{str(user_id):vote}
            }
            insert = selected_collection.insert_one(tmp)

        return tot

    def insert_stage(self, collection, category_name, news_id):
        selected_collection = self.connection[collection]
        result = selected_collection.find_one({})
        if result:
            if category_name in result:
                selected_collection.update_one({}, {"$addToSet":{category_name: int(news_id)}})
            else:
                selected_collection.update_one({}, {"$set": {category_name: [int(news_id)]}})
        else:
            tmp = {
                category_name: [int(news_id)]
            }
            selected_collection.insert_one(tmp)

