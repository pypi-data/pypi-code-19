import requests
from schatz.model import Dataset


class SchatzRest:

    def __init__(self, schatz_env):
        self.schatz_env = schatz_env
        self.schatz_env.inited = False
        self._init_user_cache()

    def _init_user_cache(self):
        json = {'username': self.schatz_env.username, 'token': self.schatz_env.token}
        response = requests.post(self._get_rest_endpoint(self.schatz_env.restUserCacheListEndpoint), json=json)
        if response.ok:
            self.schatz_env.inited = True
        else:
            raise AssertionError('Cache is not inited, status code - ' + str(response.status_code) + '. Please, ask administrators.')

    def _get_rest_endpoint(self, path='/api'):
        return 'http://' + self.schatz_env.restHost + ':' + self.schatz_env.restPort + path

    def _get_dataset_list_rest_endpoint(self):
        return self._get_rest_endpoint(self.schatz_env.restDatasetListEndpoint.replace(':username', self.schatz_env.username))

    def _get_dataset_by_name_rest_endpoint(self, dataset):
        return self._get_rest_endpoint(self.schatz_env.restDatasetByNameEndpoint.replace(':username', self.schatz_env.username).replace(':dataset', dataset))

    def list_datasets(self):
        if self.schatz_env.inited:
            results = requests.get(self._get_dataset_list_rest_endpoint(), {'token': self.schatz_env.token})
            datasets = []
            for value in results.json():
                datasets.append(Dataset(value))
            return datasets
        return None

    def get_dataset_by_name(self, name):
        if self.schatz_env.inited:
            result = requests.get(self._get_dataset_by_name_rest_endpoint(name))
            object = result.json()
            if result.status_code == 200:
                try:
                    dataset = Dataset(object)
                    return dataset
                except KeyError:
                    pass
        return None