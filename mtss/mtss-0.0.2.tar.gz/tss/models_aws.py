from datetime import datetime

import numpy as np

from models import Series as MongoSeries
from models import Slice as MongoSlice


SERIES_SCHEMA = {
    'TableName': 'Series',
    'KeySchema': [
        {
            'AttributeName': 'scope',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'name',
            'KeyType': 'RANGE'
        }
    ],
    'AttributeDefinitions': [
        {
            'AttributeName': 'scope',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'name',
            'AttributeType': 'S'
        }
    ],
    'ProvisionedThroughput': {
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
}

DATA_SCHEMA = {
    'TableName': 'Data',
    'KeySchema': [
        {
            'AttributeName': 'series_full_name',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'slice_id',
            'KeyType': 'RANGE'
        }
    ],
    'AttributeDefinitions': [
        {
            'AttributeName': 'series_full_name',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'slice_id',
            'AttributeType': 'S'
        }
    ],
    'ProvisionedThroughput': {
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
}


class Series(MongoSeries):
    def __init__(self, db, collection, scope, name, frequency, columns=[], slices=[]):
        self.db = db
        self.collection = collection
        self.scope = scope
        self.name = name
        self.full_name = Series._series_full_name(scope, name)
        self.columns = columns
        self.frequency = frequency
        self.id = self.full_name
        self.slices = {slice.id: slice for slice in slices}
        for slice in slices:
            slice.series = self
    
    @staticmethod
    def _series_full_name(scope, name):
        if scope.endswith('/'):
            return scope + name
        else:
            return scope + '/' + name

    def _generate_slice_id(self):
        return str(len(self.slices) + 1)

    def delete(self):
        for slice in self.slices.values():
            slice.delete()
        self.collection.delete_item(
            Key={'scope': self.scope, 'name': self.name}
        )

    def add_slice(self, start):
        new_slice_data = {'series_full_name': self.full_name,
                          'slice_id': self._generate_slice_id(),
                          'slice_end': time_to_str(start),
                          'num_of_samples': 0,
                          'slice_data': []}
        table = self.db.Table(DATA_SCHEMA['TableName'])
        table.put_item(Item=new_slice_data)
        slice = SparseSlice(self.db, table, start, start, new_slice_data['num_of_samples'], self, new_slice_data['slice_id'])
        new_slice = {'start': time_to_str(start),
                     'id': slice.id, 
                     'is_sparse': slice.is_sparse}
        self.collection.update_item(Key={'scope': self.scope, 'name': self.name},
                                    UpdateExpression="SET slices = list_append(slices, :i)",
                                    ExpressionAttributeValues={':i': [new_slice]},
                                    ReturnValues="UPDATED_NEW")
        self.slices[slice.id] = slice
        return slice


class SparseSlice(MongoSlice):
    def __init__(self, db, collection, start, end, num_of_samples, series=None, id=None):
        self.db = db
        self.collection = collection
        self.series = series
        self.id = id
        self.start = start
        self.end_date = end
        self.num_of_samples = num_of_samples
        self.is_sparse = True

    def add(self, data):
        if type(data) != dict:
            raise ValueError('input data is not of type dict')
        if len(data.keys()) == 0:
            return
        if not (isinstance(data.keys()[0], datetime) or isinstance(data.keys()[0], np.datetime64)):
            raise ValueError('input data key is not of type datetime')
        new_end = max(data.keys())
        data = [{'timestamp': time_to_str(d),
                 'slice_data': self._transform_data(data[d])} for d in data.keys()]
        self.collection.update_item(Key={'series_full_name': self.series.full_name, 'slice_id': self.id},
                                    UpdateExpression="SET slice_data = list_append(slice_data, :i)",
                                    ExpressionAttributeValues={':i': data},
                                    ReturnValues="UPDATED_NEW")
        self.collection.update_item(Key={'series_full_name': self.series.full_name, 'slice_id': self.id},
                                    UpdateExpression="SET num_of_samples = num_of_samples + :num",
                                    ExpressionAttributeValues={':num': len(data)},
                                    ReturnValues="UPDATED_NEW")
        if new_end > self.end:
            self.collection.update_item(Key={'series_full_name': self.series.full_name, 'slice_id': self.id},
                                        UpdateExpression="SET slice_end = :end",
                                        ExpressionAttributeValues={':end': time_to_str(new_end)},
                                        ReturnValues="UPDATED_NEW")
            self.end_date = new_end
        self.num_of_samples += len(data)

    def get(self, data_from=None, data_to=None):
        data = self.collection.get_item(Key={'series_full_name': self.series.full_name, 'slice_id': self.id})['Item']['slice_data']
        results = [[str_to_time(d['timestamp'])] + d['slice_data'] for d in data if
                   (data_from is None or str_to_time(d['timestamp']) >= data_from) and
                   (data_to is None or str_to_time(d['timestamp']) <= data_to)]
        return results

    @property
    def end(self):
        return self.end_date

    def delete(self):
        self.collection.delete_item(Key={'series_full_name': self.series.full_name, 'slice_id': self.id})
        del self.series.slices[self.id]
        self.id = None
        self.collection = None


def time_to_str(time):
    if isinstance(time, np.datetime64):
        time = time.astype(datetime)
    return time.isoformat()


def str_to_time(str):
    return np.datetime64(str)
