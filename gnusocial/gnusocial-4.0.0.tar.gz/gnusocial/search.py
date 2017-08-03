from requests import get

from .utils import _resource_url

def search(server_url, query, *args, **kwargs):
    params = kwargs.get('params', {})
    params['q'] = query
    return get(_resource_url(server_url, 'search.json'), params=params).json()
