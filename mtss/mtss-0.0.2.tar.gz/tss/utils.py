from datetime import datetime

from pymongo import MongoClient
from bson.objectid import ObjectId
import numpy as np

from config import Config as cfg
from models import Series, Slice, SparseSlice, FREQUENCIES


def get_mongo_db(config=None):
    if config is None:
        config = cfg
    client = MongoClient(config.MONGO_SERVER, config.MONGO_PORT)
    db = client[config.MONGO_DB_NAME]
    return db


def get_series(db=None, config=None, id=None):
    if db is None:
        db = get_mongo_db(config)
    if id is not None:
        if ObjectId.is_valid(id):
            cursor = db.series.find({"_id": ObjectId(id)})
        else:
            return []
    else:
        cursor = db.series.find({})
    series = [Series(db, 
                     db.series, 
                     series['_id'], 
                     series['name'], 
                     series['frequency'], 
                     series['columns'], 
                     _get_slices(db, config, series['slices'])) 
              for series in cursor]
    return series


def add_series(name, frequency, columns=[], db=None, config=None):
    if db is None:
        db = get_mongo_db(config)
    if frequency not in FREQUENCIES.keys():
        raise ValueError('frequency is not valid')
    series = db.series
    new_series = {"name": name, "frequency": frequency, "columns": columns, "slices": []}
    result = series.insert_one(new_series)
    return Series(db, series, result.inserted_id, name, frequency, columns)


def _get_slices(db=None, config=None, slices=None):
    if slices is None:
        return []
    if db is None:
        db = get_mongo_db(config)
    return [Slice(db, 
                  slice['start'], 
                  slice['num_of_samples'], 
                  None, 
                  slice.get('id', None)) for slice in slices if not slice['is_sparse']] + \
                  [SparseSlice(db, 
                               slice['start'], 
                               slice['num_of_samples'], 
                               None, 
                               slice.get('id', None)) for slice in slices if slice['is_sparse']]


def _clear_all(db=None, config=None):
    if db is None:
        db = get_mongo_db(config)
    result1 = db.series.delete_many({})
    result2 = db.data.delete_many({})
    return {'series': result1.deleted_count, 'data': result2.deleted_count}


def create_with_sparse_slices_from_df(df, name, frequency, num_of_elements_per_slice, db=None, config=None):
    if df.shape[0] == 0:
        raise ValueError('df shall not be empty')
    
    first_index_value = df.iloc[0].name
    if not isinstance(first_index_value, datetime) and not isinstance(first_index_value, np.datetime64):
        raise ValueError("df's index can only either be of type datetime.datetime or numpy.datetime64")
    
    df.sort_index(inplace=True)
        
    series = add_series(name, frequency, list(df.columns), db, config)
    
    for chunk in (df[pos:pos + num_of_elements_per_slice] for pos in xrange(0, df.shape[0], num_of_elements_per_slice)):
        sparse_slice = series.add_slice(chunk.iloc[0].name, is_sparse=True)
        data = chunk.to_dict(orient='index')
        sparse_slice.add(data)
    return series
