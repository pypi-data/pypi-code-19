from pytest_mock import mocker

from hudai.client import HudAi
from hudai.resource import Resource

client = HudAi('mock-api-key')

def test_inherited_resource_methods(mocker):
    resource = Resource(client)

    assert callable(resource.request)


def test_request(mocker):
    mocker.patch.object(client, 'make_request', autospec=True)
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

    client.make_request.assert_called_once_with(method, url, params, data)


def test_request_defaults(mocker):
    mocker.patch.object(client, 'make_request', autospec=True)
    resource = Resource(client)

    resource.request({ 'url': '/test/path' })

    client.make_request.assert_called_once_with('GET', '/test/path', {}, {})


def test_request_path_building(mocker):
    client.make_request = mocker.stub(name='make_request')
    resource = Resource(client)

    params = { 'replace_me': 'foo' }

    resource.request({ 'url': '/test/{replace_me}/path', 'params': params })

    client.make_request.assert_called_once_with('GET', '/test/foo/path', params, {})
