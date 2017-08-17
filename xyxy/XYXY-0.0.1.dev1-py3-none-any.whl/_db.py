import json

from pymongo import MongoClient

from . import _config


def import_json_to_db(file, db):
    with open(file, 'r') as f:
        meta = db.insert_many(json.load(f))
        return meta.inserted_ids


def get_indices_from_db(db):
    return db.find({}).distinct('_id')

def connect(mongo_uri=None):
    if mongo_uri is not None:
        _config.MONGO_DB = MongoClient(mongo_uri)[_config.MONGO_DBNAME]
    else:
        _config.MONGO_DB = MongoClient('mongodb://localhost:27017')[_config.MONGO_DBNAME]
