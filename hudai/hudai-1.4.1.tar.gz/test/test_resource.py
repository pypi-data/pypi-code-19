from pytest_mock import mocker

from hudai.client import HudAi
from hudai.resource import Resource

client = HudAi(api_key='mock-api-key')

def test_inherited_resource_methods(mocker):
    resource = Resource(client)

    assert callable(resource.request)


def test_request(mocker):
    mocker.patch.object(client, 'get', autospec=True)
    resource = Resource(client)

    method = 'GET'
    params = { 'test': 'param' }
    data = { 'test': 'data' }
    url = '/test/path'

    resource.request({
        'method': method,
        'url': url,
        'params': params,
        'data': data
    })

    client.get.assert_called_once_with(url, params=params, data=data)


def test_request_defaults(mocker):
    mocker.patch.object(client, 'get', autospec=True)
    resource = Resource(client)

    resource.request({ 'url': '/test/path' })

    client.get.assert_called_once_with('/test/path', params={}, data={})


def test_request_path_building(mocker):
    mocker.patch.object(client, 'get', autospec=True)
    resource = Resource(client)

    params = { 'replace_me': 'foo' }

    resource.request({ 'url': '/test/{replace_me}/path', 'params': params })

    client.get.assert_called_once_with('/test/foo/path', params=params, data={})
