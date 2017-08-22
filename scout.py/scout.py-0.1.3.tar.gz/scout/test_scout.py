import requests
import unittest
import uuid
import os

from unittest import mock
from .scout import Scout

install_id = str(uuid.uuid4())


# This method will be used by the mock to replace requests.get
def mocked_requests_post(*args, **kwargs):

    apps = {'foshizzolator'}
    latest_version = '0.2.0'

    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    app = kwargs["json"]["application"]
    if app not in apps:
        return MockResponse(None, 404)

    return MockResponse({"latest_version": latest_version}, 200)


class ScoutTestCase(unittest.TestCase):

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_disable_by_SCOUT_DISABLE_environment_variable(self, mock_post):
        for v in {"1", "true", "yes"}:
            os.environ["SCOUT_DISABLE"] = v

            scout = Scout(app="unknown", version="0.1.0", install_id=install_id)
            scout.report()

            self.assertFalse(mock_post.called)
            del os.environ["SCOUT_DISABLE"]

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_disable_by_TRAVIS_REPO_SLUG_environment_variable(self, mock_post):
        os.environ["TRAVIS_REPO_SLUG"] = "datawire/foobar"

        scout = Scout(app="unknown", version="0.1.0", install_id=install_id)
        scout.report()

        self.assertFalse(mock_post.called)
        del os.environ["TRAVIS_REPO_SLUG"]

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_report_for_unknown_app(self, mock_post):
        
        """When the app is unknown scout will return an HTTP 404 but the report function should just act normally"""
        
        scout = Scout(app="unknown", version="0.1.0", install_id=install_id)
        resp = scout.report()

        self.assertEqual(resp, {"latest_version": "0.1.0"})

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_report(self, mock_post):

        """Scout backend returns the latest version. The scout client returns this to the caller."""

        scout = Scout(app="foshizzolator", version="0.1.0", install_id=install_id)
        resp = scout.report()

        self.assertEqual(resp, {"latest_version": "0.2.0"})


if __name__ == '__main__':
    unittest.main()
