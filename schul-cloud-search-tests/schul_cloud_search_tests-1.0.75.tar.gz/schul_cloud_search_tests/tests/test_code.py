"""
For AGPL compatibility, we want to test the ability to view the code.
This is especially useful if we want to debug the application.
Suppose a test runs locally but not in the container.
There, we need to examine the versions of the tests.

The endpoints are
/source/...
  with listings and files
/source.zip -> /schul_cloud_search_tests.zip
  a zip file of the source code
"""
import requests
from pytest import mark
import os

HERE = os.path.dirname(__file__)


@mark.parametrize("directory,content", [
        ("/", ["proxy.py"]),
        ("/tests/", ["__init__.py", "conftest.py", "test_code.py", "README.rst"]),
        ("/search_tests/", ["__init__.py", "conftest.py", "test_links.py", "README.rst"]),
    ])
@mark.parametrize("appendix", ["", "/"])
def test_directories_are_listed(code_url, appendix, directory, content):
    """Make sure the files listed to view them."""
    text = requests.get(code_url + appendix).text
    print(text)
    for entry in content:
        included_text = "<a href=\"/code{}{}\"".format(directory, entry)
        assert included_text in text


@mark.parametrize("file,url", [
        ("test_code.py", "/tests/test_code.py"),
        ("../proxy.py", "/proxy.py")
    ])
def test_can_download_files(code_url, file, url):
    """Download the zip file of all files."""
    with open(os.path.join(HERE, file)) as f:
        expected_text = f.read()
    response = requests.get(code_url + url)
    assert response.text == expected_text


def test_can_download_joined_zip_file(code_url):
    """The request to /code.zip redirects to the package name zip file."""
    response = requests.get(code_url + ".zip")
    assert response.url.endswith("schul_cloud_search_tests.zip")


def test_listing_links_to_repository(code_url):
    """The link to the repository is included in the listing."""
    response = requests.get(code_url)
    assert "<a href=\"https://github.com/schul-cloud/schul_cloud_search_tests\"" in response.text


def test_source_code_download_link_is_in_listing(code_url):
    """Make sure users can download the current code."""
    response = requests.get(code_url)
    assert "<a href=\"/code.zip\"" in response.text


def test_source_link_of_search_engine_refers_to_source_endpoint(
        search_engine, code_url):
    """Test that the source link of the response of the search engine
    refers to the code enpoint /code of the same search engine."""
    response = search_engine.request({})
    source = response.json()["jsonapi"]["meta"]["source"]
    assert source == code_url
