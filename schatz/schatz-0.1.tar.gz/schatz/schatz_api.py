from os import getenv

import requests
import sqlalchemy as sa

from schatz.schatz_model import Dataset

class SchatzApi:

    def __init__(self):
        self._storageHost = getenv('SCHATZ_STORAGE_HOST', 'localhost')
        self._storagePort = getenv('SCHATZ_STORAGE_PORT', '8090')
        self._restHost = getenv('SCHATZ_REST_HOST', 'localhost')
        self._restPort = getenv('SCHATZ_REST_PORT', '8091')
        self._restDataTableListEndpoint = getenv('SCHATZ_REST_DATA_TABLE_LIST_ENDPOINT', '/api/dataTable/:username')
        self._token = getenv('SCHATZ_TOKEN', 'need-token')
        self._username = getenv('SCHATZ_USER', 'user')

        self._sqlEngine = sa.create_engine(self._get_storage_endpoint(self._token))

    def _get_storage_endpoint(self, token):
        return 'clickhouse://@' + self._storageHost + ':' + self._storagePort + '/' + token

    def _get_rest_endpoint(self, path='/api'):
        return 'http://' + self._restHost + ':' + self._restPort + path

    def _get_data_table_list_rest_endpoint(self):
        return self._get_rest_endpoint(self._restDataTableListEndpoint.replace(':username', self._username))

    def list_datasets(self):
        results = requests.get(self._get_data_table_list_rest_endpoint(), {'token': self._token})
        datasets = []
        for value in results.json():
            datasets.append(Dataset(value))
        return datasets

    def connect_sql_alchemy(self):
        return self._sqlEngine.connect()

    def get_table_name_with_token(self, dataset):
        return self._token + "." + dataset.name
