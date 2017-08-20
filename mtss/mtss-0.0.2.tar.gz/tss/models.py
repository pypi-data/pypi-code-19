from datetime import datetime

import numpy as np
import pandas as pd

from . import FREQUENCIES


class Series(object):
    def __init__(self, db, collection, objectId, name, frequency, columns=[], slices=[]):
        self.db = db
        self.collection = collection
        self.id = objectId
        self.name = name
        self.columns = columns
        self.frequency = frequency
        self.slices = {slice.id: slice for slice in slices}
        for slice in slices:
            slice.series = self
        
    def delete(self):
        for slice in self.slices.values():
            slice.delete()
        self.collection.delete_one({"_id": self.id})
        self.id = None
        
    def add_slice(self, start, num_of_samples = 0, is_sparse=False):
        result = self.db.data.insert_one({'data': []})
        if is_sparse:
            slice = SparseSlice(self.db, start, num_of_samples, self, result.inserted_id)
        else:
            slice = Slice(self.db, start, num_of_samples, self, result.inserted_id)       
        self.collection.update({'_id': self.id}, 
                               {"$push": {"slices": {'start': start, 
                                                     'num_of_samples': num_of_samples, 
                                                     'id': slice.id, 
                                                     'is_sparse': slice.is_sparse}}},
                               upsert=False)
        self.slices[slice.id] = slice
        return slice
    
    def find_slice_starts_at(self, datetime):
        return filter(self.slices, lambda s: s.start == datetime)
    
    def get(self, data_from=None, data_to=None):
        results = pd.DataFrame(columns=self.columns + ['time'])
        for s in self.slices.values():
            start = s.start
            end = s.end
            if data_from is not None and data_from > start:
                start = data_from
            if data_to is not None and data_to < end:
                end = data_to
            if start > end:
                data = []
            else:
                data = s.get(start, end)
            if data == []:
                continue
            slice_df = pd.DataFrame(data, columns=['time'] + self.columns)
            results = results.append(slice_df)
        results.set_index('time', inplace=True)
        results.sort_index(inplace=True)
        return results
    
    def __repr__(self):
        return 'Series[id={}, name={}, columns={}, frequency={}]'.format(self.id, self.name, self.columns, self.frequency)


class Slice(object):
    def __init__(self, db, start, num_of_samples, series = None, id = None):
        self.db = db
        self.collection = db.data
        self.series = series
        self.id = id
        self.start = start
        self.num_of_samples = num_of_samples
        self.is_sparse = False
    
    def add(self, data):
        if type(data) != list:
            raise ValueError("input data is not of type list")
        if len(data) == 0:
            return
        if isinstance(data[0], dict):
            data = [self._transform_data(d) for d in data]
        self.collection.update({'_id': self.id}, 
                               {'$push': {'data': {'$each': data}}})
        self.series.collection.update({'_id': self.series.id,
                                       'slices.id': self.id},
                                      {'$inc': {'slices.$.num_of_samples': len(data)}})
        self.num_of_samples += len(data)
        
    def _transform_data(self, data):
        columns = self.series.columns
        if isinstance(data, dict):
            return [data[c] for c in columns]
        else:
            return data
        
    def get(self, data_from=None, data_to=None):
        if self.num_of_samples == 0:
            return []
        frequency = FREQUENCIES[self.series.frequency]
        data = self.collection.find({'_id': self.id}, {'data': 1}).limit(1)[0]['data']
        start = np.datetime64(self.start)
        timestamps = [start + i * frequency for i in xrange(0, self.num_of_samples)]
        results = zip(timestamps, data)
        if data_from is not None:
            data_from = np.datetime64(data_from)
        else:
            data_from = start
        if data_to is not None:
            data_to = np.datetime64(data_to)
        else:
            data_to = timestamps[-1]
        return [[r[0]] + r[1] for r in results if r[0] >= data_from and r[0] <= data_to]
    
    @property
    def end(self):
        frequency = FREQUENCIES[self.series.frequency]
        start = np.datetime64(self.start)
        return (start + self.num_of_samples * frequency).astype(datetime)
        
    def delete(self):
        self.collection.delete_one({"_id": self.id})
        del self.series.slices[self.id]
        self.id = None
        
    def __repr__(self):
        return 'Slice[id={}, start={}, number_of_samples={}, is_sparse={}]'.format(self.id, 
                                                                                   self.start, 
                                                                                   self.num_of_samples, 
                                                                                   self.is_sparse)
    
    
class SparseSlice(Slice):
    def __init__(self, db, start, num_of_samples, series = None, id = None):
        super(SparseSlice, self).__init__(db, start, num_of_samples, series, id)
        self.is_sparse = True
    
    def add(self, data):
        if type(data) != dict:
            raise ValueError('input data is not of type dict')
        if len(data.keys()) == 0:
            return
        if not (isinstance(data.keys()[0], datetime) or isinstance(data.keys()[0], np.datetime64)):
            raise ValueError('input data key is not of type datetime')
        data = [{'timestamp': SparseSlice._format_timestamp(d), 
                 'data': self._transform_data(data[d])} for d in data.keys()]
        self.collection.update({'_id': self.id}, 
                               {'$push': {'data': {'$each': data}}})
        self.series.collection.update({'_id': self.series.id,
                                       'slices.id': self.id},
                                      {'$inc': {'slices.$.num_of_samples': len(data)}})
        self.num_of_samples += len(data)
     
    @staticmethod
    def _format_timestamp(time):
        if isinstance(time, np.datetime64):
            return time.astype(datetime)
        else:
            return time
        
    def get(self, data_from=None, data_to=None):
        if self.num_of_samples == 0:
            return []
        data = self.collection.find({'_id': self.id}, {'data': 1}).limit(1)[0]['data']
        results = [[np.datetime64(d['timestamp'])] + d['data'] for d in data if 
                   (data_from is None or d['timestamp'] >= data_from) and 
                   (data_to is None or d['timestamp'] <= data_to)]
        return results
    
    @property
    def end(self):
        if self.num_of_samples == 0:
            return self.start
        results = self.collection.aggregate([{'$match': {'_id': self.id}},
                                             {'$unwind': '$data'},
                                             {'$sort': {'data.timestamp': -1}},
                                             {'$limit': 1}])
        return [r['data']['timestamp'] for r in results if r['_id'] == self.id][0]
