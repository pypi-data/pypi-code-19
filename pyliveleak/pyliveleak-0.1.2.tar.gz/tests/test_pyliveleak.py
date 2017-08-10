#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `pyliveleak` package."""
import codecs
import io
import os.path as P

import mock
import pytest

from click.testing import CliRunner

from pyliveleak import pyliveleak
from pyliveleak import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help' in help_result.output


def read_html(name):
    curr_dir = P.dirname(__file__)
    path = P.join(curr_dir, 'test-data', name)
    with codecs.open(path, 'r', pyliveleak._TEXT_ENCODING) as fin:
        return fin.read()


def test_add_item_parses_multipart_params():
    page = pyliveleak.AddItemPage(read_html('add_item.html'), {})
    params = page.multipart_params
    #
    # The name field gets appended by us later.
    #
    actual = {field: field in params for field in pyliveleak._MULTIPART_FIELDS
              if field != 'name'}
    expected = {field: True for field in actual}
    assert expected == actual


def test_add_item_parses_connection():
    page = pyliveleak.AddItemPage(read_html('add_item.html'), {})
    assert page.connection == '09b_1502291107'


def test_add_item_parses_connect_string():
    page = pyliveleak.AddItemPage(read_html('add_item.html'), {})
    assert page.connect_string is not None


@mock.patch('pyliveleak.pyliveleak.open', mock.Mock(return_value=io.BytesIO(b'foo')))
@mock.patch(
    'requests.post',
    mock.Mock(return_value=mock.Mock(text=read_html('llbucs.html'), status_code=201))
)
def test_add_item_upload_to_aws():
    page = pyliveleak.AddItemPage(read_html('add_item.html'), {})
    aws_response = page.upload_to_aws('/dummy/file')
    expected = {field: True for field in ('Bucket', 'ETag', 'Key', 'Location')}
    actual = {field: field in aws_response for field in expected}
    assert expected == actual


@pytest.fixture
@mock.patch('pyliveleak.pyliveleak.open', mock.Mock(return_value=io.BytesIO(b'foo')))
def page_after_upload():
    page = pyliveleak.AddItemPage(read_html('add_item.html'), {})
    with mock.patch('requests.post') as mock_post:
        mock_post.return_value.text = read_html('llbucs.html')
        mock_post.return_value.status_code = 201
        aws_response = page.upload_to_aws('/dummy/file')
    return page, aws_response


@mock.patch('pyliveleak.pyliveleak.open', mock.Mock(return_value=io.BytesIO(b'foo')))
def test_add_item_add_file():
    page, aws_response = page_after_upload()
    with mock.patch('requests.get') as mock_get:
        mock_get.return_value.text = read_html('file.html')
        file_token = page.add_file('/dummy/file', aws_response)
    assert file_token == '0a84eec3c572'


def test_add_item_add_file_404():
    page, aws_response = page_after_upload()
    with mock.patch('requests.get') as mock_get:
        mock_get.return_value.text = 'Not found'
        mock_get.return_value.status_code = 404
        pytest.raises(pyliveleak.PyLiveleakException, page.add_file,
                      '/dummy/file', aws_response)


def test_add_item_add_file_not_json():
    page, aws_response = page_after_upload()
    with mock.patch('requests.get') as mock_get:
        mock_get.return_value.text = 'not valid json'
        mock_get.return_value.status_code = 200
        pytest.raises(pyliveleak.PyLiveleakException, page.add_file,
                      '/dummy/file', aws_response)


def test_add_item_add_file_fail():
    page, aws_response = page_after_upload()
    with mock.patch('requests.get') as mock_get:
        mock_get.return_value.text = '{"success": "no", "msg": "Haha"}'
        mock_get.return_value.status_code = 200
        pytest.raises(pyliveleak.PyLiveleakException, page.add_file,
                      '/dummy/file', aws_response)


def test_add_item_publish():
    page, _ = page_after_upload()
    with mock.patch('requests.post') as mock_post:
        mock_post.return_value.text = read_html('add_item.json')
        item_token = page.publish('/dummy/file')
    assert item_token == '09b_1502291107'


def test_add_item_publish_fail():
    page, _ = page_after_upload()
    with mock.patch('requests.post') as mock_post:
        mock_post.return_value.text = '{"success": 0, "msg": "You Fail"}'
        pytest.raises(pyliveleak.PyLiveleakException, page.publish, '/file')


def test_add_item_publish_not_json():
    page, _ = page_after_upload()
    with mock.patch('requests.post') as mock_post:
        mock_post.return_value.text = 'not json'
        pytest.raises(pyliveleak.PyLiveleakException, page.publish, '/file')


@mock.patch('pyliveleak.pyliveleak.open', mock.Mock(return_value=io.BytesIO(b'foo')))
def test_encode_fields():
    page = pyliveleak.AddItemPage(read_html('add_item.html'), {})
    headers, data = pyliveleak._encode_fields('/dummy/path', page.multipart_params)
    assert headers['Host'] == 'llbucs.s3.amazonaws.com'
