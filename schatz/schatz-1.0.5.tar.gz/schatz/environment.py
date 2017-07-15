from os import getenv


class SchatzEnv:

    def __init__(self):
        self.storageHost = getenv('SCHATZ_STORAGE_HOST', 'localhost')
        self.storagePort = getenv('SCHATZ_STORAGE_PORT', '8090')
        self.restHost = getenv('SCHATZ_REST_HOST', 'localhost')
        self.restPort = getenv('SCHATZ_REST_PORT', '8091')
        self.restDatasetListEndpoint = getenv('SCHATZ_REST_DATA_TABLE_LIST_ENDPOINT', '/api/dataTable/:username')
        self.restDatasetByNameEndpoint = getenv('SCHATZ_REST_DATA_TABLE_LIST_ENDPOINT', '/api/dataTable/:username/:dataset')
        self.restUserCacheListEndpoint = getenv('SCHATZ_REST_USER_CACHE_LIST_ENDPOINT', '/api/userCache')
        self.token = getenv('SCHATZ_TOKEN', 'need-token')
        self.username = getenv('SCHATZ_USER', 'user')
        self.inited = False

    def get_storage_endpoint(self):
        return 'clickhouse://@' + self.storageHost + ':' + self.storagePort + '/' + self.token