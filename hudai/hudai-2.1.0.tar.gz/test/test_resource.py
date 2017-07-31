import pytest
from pytest_mock import mocker

from hudai.client import HudAi
from hudai.resource import Resource

client = HudAi(api_key='mock-api-key')


def test_standard_http_verbs_available():
    resource = Resource(client)

    assert callable(resource.get)
    assert callable(resource.post)
    assert callable(resource.put)
    assert callable(resource.patch)
    assert callable(resource.delete)


@pytest.mark.parametrize('http_verb', [('get'),('post'),('put'),('patch'),('delete')])
def test_setting_base_path(mocker, http_verb):
    mocker.patch.object(client, http_verb, autospec=True)
    resource = Resource(client, base_path='/test')

    function_under_test = getattr(resource, http_verb)
    client_function = getattr(client, http_verb)

    function_under_test('/foo/bar', {})

    client_function.assert_called_once_with('/test/foo/bar')


@pytest.mark.parametrize('http_verb', [('get'),('post'),('put'),('patch'),('delete')])
def test_parameter_injection(mocker, http_verb):
    mocker.patch.object(client, http_verb, autospec=True)
    resource = Resource(client)

    function_under_test = getattr(resource, http_verb)
    client_function = getattr(client, http_verb)

    function_under_test('/test/{replace_me}/path',
                        {'params': {'replace_me': 'replaced'}})

    client_function.assert_called_once_with('/test/replaced/path')


def test__list(mocker):
    mocker.patch.object(client, 'get', autospec=True)
    resource = Resource(client, base_path='/mock-resource')

    resource._list(foo='bar')

    client.get.assert_called_once_with('/mock-resource/', query_params={ 'foo' : 'bar' })


def test__create(mocker):
    mocker.patch.object(client, 'post', autospec=True)
    resource = Resource(client, base_path='/mock-resource')

    resource._create(foo='bar')

    client.post.assert_called_once_with('/mock-resource/', data={ 'foo' : 'bar' })


def test__get(mocker):
    mocker.patch.object(client, 'get', autospec=True)
    resource = Resource(client, base_path='/mock-resource')

    resource._get('fake-uuid')

    client.get.assert_called_once_with('/mock-resource/fake-uuid')


def test__update(mocker):
    mocker.patch.object(client, 'put', autospec=True)
    resource = Resource(client, base_path='/mock-resource')

    resource._update('fake-uuid', foo='bar')

    client.put.assert_called_once_with('/mock-resource/fake-uuid', data={ 'foo' : 'bar' })


def test__delete(mocker):
    mocker.patch.object(client, 'delete', autospec=True)
    resource = Resource(client, base_path='/mock-resource')

    resource._delete('fake-uuid')

    client.delete.assert_called_once_with('/mock-resource/fake-uuid')
