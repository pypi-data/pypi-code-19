"""HUD.ai Resource Specs

Resources define collections of actions that can be performed on the same object
set (e.g. a User), and include a set of common (inheritable) protected methods
around CRUD actions.
"""
import pytest
from pytest_mock import mocker

from hudai.client import HudAi
from hudai.resource import Resource

client = HudAi(api_key='mock-api-key')


def test_standard_http_verbs_available():
    resource = Resource(client)

    assert callable(resource.http_get)
    assert callable(resource.http_post)
    assert callable(resource.http_put)
    assert callable(resource.http_patch)
    assert callable(resource.http_delete)


@pytest.mark.parametrize('http_verb', [('get'), ('post'), ('put'), ('patch'), ('delete')])
def test_setting_base_path(mocker, http_verb):
    """
    Ensure that the `base_path` given when the resource is initialized is
    injected into all requests performed by that resource
    """
    method_name = "http_{}".format(http_verb)
    mocker.patch.object(client, method_name, autospec=True)
    resource = Resource(client, base_path='/test')

    function_under_test = getattr(resource, method_name)
    client_function = getattr(client, method_name)

    function_under_test('/foo/bar', params={})

    client_function.assert_called_once_with('/test/foo/bar')


@pytest.mark.parametrize('http_verb', [('get'), ('post'), ('put'), ('patch'), ('delete')])
def test_parameter_injection(mocker, http_verb):
    """
    Ensure that the resource injects `params` into the URL when there is a
    matching keyword
    """
    method_name = "http_{}".format(http_verb)
    mocker.patch.object(client, method_name, autospec=True)
    resource = Resource(client)

    function_under_test = getattr(resource, method_name)
    client_function = getattr(client, method_name)

    function_under_test('/test/{replace_me}/path',
                        params={'replace_me': 'replaced'})

    client_function.assert_called_once_with('/test/replaced/path')


def test__list(mocker):
    """
    Ensure that the inheritable method `_list` acts as expected
    (performs GET with params)
    """
    mocker.patch.object(client, 'http_get', autospec=True)
    resource = Resource(client, base_path='/mock-resource')

    resource._list(foo='bar')

    client.http_get.assert_called_once_with('/mock-resource/',
                                            query_params={'foo': 'bar'})


def test__create(mocker):
    """
    Ensure that the inheritable method `_create` acts as expected
    (performs POST with params)
    """
    mocker.patch.object(client, 'http_post', autospec=True)
    resource = Resource(client, base_path='/mock-resource')

    resource._create(foo='bar')

    client.http_post.assert_called_once_with('/mock-resource/',
                                             data={'foo': 'bar'})


def test__fetch(mocker):
    """
    Ensure that the inheritable method `_fetch` acts as expected
    (performs GET action for given ID)
    """
    mocker.patch.object(client, 'http_get', autospec=True)
    resource = Resource(client, base_path='/mock-resource')

    resource._fetch('fake-uuid')

    client.http_get.assert_called_once_with('/mock-resource/fake-uuid')


def test__update(mocker):
    """
    Ensure that the inheritable method `_update` acts as expected
    (performs PUT action for given ID, passing data)
    """
    mocker.patch.object(client, 'http_put', autospec=True)
    resource = Resource(client, base_path='/mock-resource')

    resource._update('fake-uuid', foo='bar')

    client.http_put.assert_called_once_with('/mock-resource/fake-uuid',
                                            data={'foo': 'bar'})


def test__delete(mocker):
    """
    Ensure that the inheritable method `_delete` acts as expected
    (performs DELETE action for given ID)
    """
    mocker.patch.object(client, 'http_delete', autospec=True)
    resource = Resource(client, base_path='/mock-resource')

    resource._delete('fake-uuid')

    client.http_delete.assert_called_once_with('/mock-resource/fake-uuid')
