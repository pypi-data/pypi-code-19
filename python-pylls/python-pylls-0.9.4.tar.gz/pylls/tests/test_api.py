#
#    Cachet API python client and interface (python-pylls)
#
#    Copyright (C) 2017 Denis Pompilio (jawa) <denis.pompilio@gmail.com>
#
#    This file is part of python-pylls
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, see <http://www.gnu.org/licenses/>.

import os
import logging
import json
from functools import partialmethod
from requests.exceptions import HTTPError
from urllib.parse import urlparse, parse_qs

import pytest
from unittest.mock import MagicMock

from . import resources
from pylls import client
from pylls import cachet


API_CLIENT = None
API_ENDPOINT = os.environ.get('API_ENDPOINT', 'https://status/api/v1')
API_TOKEN = os.environ.get('API_TOKEN', 'XXXXXXXXXXX')
CFG = {
    'api_endpoint': API_ENDPOINT,
    'api_token': API_TOKEN
}


class MockSession(MagicMock):
    """Provide a test request.Session object"""

    log = logging.getLogger('unittests')

    def get_uriparams(self, base, path):
        """Split URI on base path"""
        self.log.debug('call: ' + str((base, path)))
        url_o = urlparse(path)
        path = url_o.path.replace(base, '')
        params = parse_qs(url_o.query)
        if not len(path) or path == '/':
            p_params = []
        else:
            p_params = path.split('/')[1:]

        self.log.debug('urlparse result: ' + str((p_params, params)))
        return p_params, params

    def paginate(self, url, entries, page):
        """Mock pagination"""
        url = API_ENDPOINT + url
        reply = {
            'data': [entries[page-1]],
            'meta': resources.meta_pagination(url, len(entries), page)
        }
        return self.respond(reply)

    @staticmethod
    def respond(data, raise_exc=None):
        """Respond a mock object"""
        mock = MagicMock()
        if len(data['data']):
            mock.json = MagicMock(return_value=data)
        else:
            mock.json = MagicMock(side_effect=ValueError('Invalid json'))
        mock.text = str(data)
        if raise_exc is not None:
            mock.raise_for_status = MagicMock(side_effect=raise_exc)
        return mock

    def request(self, method, url, data=None, **kwargs):
        """Mock method to simulate the Cachet API behavior"""
        # Strip endpoint base from url
        url = url.replace(API_ENDPOINT, '')
        url = url.replace('//', '/')
        self.log.debug('call:' + str((method, url, data, kwargs)))
        if url.startswith("/ping"):
            return self.ping(method, url, data)
        elif url.startswith("/version"):
            return self.version(method, url, data)
        elif url.startswith("/components/groups"):
            return self.components_groups(method, url, data)
        elif url.startswith("/components"):
            return self.components(method, url, data)
        elif url.startswith("/incidents"):
            return self.incidents(method, url, data)
        elif ['metrics', 'points'] == url.split("/")[1:4:2]:
            return self.points(method, url, data)
        elif url.startswith("/metrics"):
            return self.metrics(method, url, data)
        elif url.startswith("/subscribers"):
            return self.subscribers(method, url, data)
        return self.respond({'data': ''}, HTTPError('API error'))

    def validate_query_params(self, endpoint, method, params):
        """Validate query parameters"""
        self.log.debug("call: " + str((endpoint, method, params)))
        return True

    def endpoint(self, endpoint_path, entries, method, url, data):
        """Mock endpoints

        :param str endpoint_path: Endpoint path
        :param str method: HTTP method
        :param str url: URL called
        :param dict data: Data post
        :param dict entries: Entries returned by mock endpoint
        :return: Mock API response as Mock request object
        """
        data = json.loads(data)
        p_params, params = self.get_uriparams(endpoint_path, url)
        url = url.split('?')[0]
        if method == "GET":
            res = entries
            if len(p_params):
                try:
                    res = entries[int(p_params[0]) - 1]
                except IndexError:
                    return self.respond({'data': ''}, HTTPError('API error'))
            if 'per_page' in data or 'page' in params:
                page = int(params.get('page', [1])[0])
                return self.paginate(url, res, page)
            return self.respond({'data': res})
        elif method == "POST":
            assert self.validate_query_params(endpoint_path, method, data)
            return self.respond({'data': entries[0]})
        elif method == "PUT" and len(p_params):
            assert self.validate_query_params(endpoint_path, method, data)
            try:
                return self.respond({'data': entries[int(p_params[0]) - 1]})
            except IndexError:
                return self.respond({'data': ''}, HTTPError('API error'))
        elif method == "DELETE" and len(p_params):
            return self.respond({'data': ''})
        return self.respond({'data': ''}, HTTPError('API error'))

    def ping(self, method, url, data):
        """Mock /ping endpoint"""
        self.log.debug('call: ' + str((method, url, data)))
        if method == "GET":
            return self.respond({'data': 'Pong!'})
        return self.respond({'data': ''}, HTTPError('API error'))

    def version(self, method, url, data):
        """Mock /version endpoint"""
        self.log.debug('call: ' + str((method, url, data)))
        if method == "GET":
            return self.respond({'data': '2.3.10',
                                 'meta': {
                                     'latest': {
                                         'tag_name': 'v2.3.12',
                                         'prelease': False,
                                         'draft': False},
                                     'on_latest': True}})

    def points(self, method, url, data):
        """Mock /metrics/XX/points endpoint"""
        endpoint_path = '/'.join(url.split('/')[:4])
        return self.endpoint(endpoint_path, resources.POINTS,
                             method, url, data)

    components_groups = partialmethod(endpoint, "/components/groups",
                                      resources.COMPONENT_GROUPS)
    components = partialmethod(endpoint, "/components", resources.COMPONENTS)
    incidents = partialmethod(endpoint, "/incidents", resources.INCIDENTS)
    metrics = partialmethod(endpoint, "/metrics", resources.METRICS)
    subscribers = partialmethod(endpoint, "/subscribers",
                                resources.SUBSCRIBERS)


@pytest.fixture()
def api_client():
    global API_CLIENT
    if API_CLIENT is None:
        API_CLIENT = client.CachetAPIClient(**CFG)
        API_CLIENT.r_session = MockSession()
    return API_CLIENT


def test_api_ping(api_client):
    """Test Ping endpoint"""
    response = cachet.Ping(api_client).get()
    assert 'Pong!' in response


def test_api_version(api_client):
    """Test Version endpoint"""
    response = cachet.Version(api_client).get()
    (major, minor, bugfix) = response.split('.')
    assert (0, 0, 0) <= (int(major), int(minor), int(bugfix))


def test_component_groups_list(api_client):
    components = cachet.Components(api_client)
    groups_list = list(components.groups.get())
    assert len(groups_list) == 3


def test_component_groups_list_paginated(api_client):
    components = cachet.Components(api_client)
    groups_list = list(components.groups.get(per_page=1))
    assert len(groups_list) == 3


def test_component_groups_get(api_client):
    components = cachet.Components(api_client)
    group = list(components.groups.get(1))[0]
    assert group['name'] == "Group A"


def test_component_groups_create(api_client):
    components = cachet.Components(api_client)
    created = components.groups.create("Group A")
    assert created['name'] == "Group A"


def test_component_groups_update(api_client):
    components = cachet.Components(api_client)
    updated = components.groups.update(1, "Group A")
    assert updated['name'] == "Group A"


def test_component_groups_delete(api_client):
    components = cachet.Components(api_client)
    components.groups.delete(1)
    return True


def test_components_list(api_client):
    components = cachet.Components(api_client)
    components_list = list(components.get())
    assert len(components_list) == 6


def test_components_list_paginated(api_client):
    components = cachet.Components(api_client)
    components_list = list(components.get(per_page=1))
    assert len(components_list) == 6


def test_components_get(api_client):
    components = cachet.Components(api_client)
    component = list(components.get(1))[0]
    assert component['name'] == "Component A"


def test_components_create(api_client):
    components = cachet.Components(api_client)
    created = components.create("Component A", 1)
    assert created['name'] == "Component A"


def test_components_update(api_client):
    components = cachet.Components(api_client)
    updated = components.update(1, "Component A")
    assert updated['name'] == "Component A"


def test_components_delete(api_client):
    components = cachet.Components(api_client)
    components.delete(1)
    return True


def test_incidents_list(api_client):
    incidents = cachet.Incidents(api_client)
    incidents_list = list(incidents.get())
    assert len(incidents_list) == 6


def test_incidents_list_paginated(api_client):
    incidents = cachet.Incidents(api_client)
    incidents_list = list(incidents.get(per_page=1))
    assert len(incidents_list) == 6


def test_incidents_get(api_client):
    incidents = cachet.Incidents(api_client)
    incident = list(incidents.get(1))[0]
    assert incident['name'] == "Incident 1"


def test_incidents_create(api_client):
    incidents = cachet.Incidents(api_client)
    created = incidents.create("Incident 1", "Test incident 1.", 1, 1)
    assert created['name'] == "Incident 1"


def test_incidents_update(api_client):
    incidents = cachet.Incidents(api_client)
    updated = incidents.update(1, "Incident 1")
    assert updated['name'] == "Incident 1"


def test_incidents_delete(api_client):
    incidents = cachet.Incidents(api_client)
    incidents.delete(1)
    return True


def test_metrics_list(api_client):
    metrics = cachet.Metrics(api_client)
    metrics_list = list(metrics.get())
    assert len(metrics_list) == 2


def test_metrics_list_paginated(api_client):
    metrics = cachet.Metrics(api_client)
    metrics_list = list(metrics.get(per_page=1))
    assert len(metrics_list) == 2


def test_metrics_get(api_client):
    metrics = cachet.Metrics(api_client)
    metric = list(metrics.get(1))[0]
    assert metric['name'] == "Metric 1"


def test_metrics_create(api_client):
    metrics = cachet.Metrics(api_client)
    created = metrics.create("Metric 1", "Test metric 1.", 1, 1)
    assert created['name'] == "Metric 1"


def test_metrics_delete(api_client):
    metrics = cachet.Metrics(api_client)
    metrics.delete(1)
    return True


def test_points_list(api_client):
    metrics = cachet.Metrics(api_client)
    points_list = list(metrics.points.get(1))
    assert len(points_list) == 2


def test_points_list_paginated(api_client):
    metrics = cachet.Metrics(api_client)
    points_list = list(metrics.points.get(1, per_page=1))
    assert len(points_list) == 2


def test_points_create(api_client):
    metrics = cachet.Metrics(api_client)
    created = metrics.points.create(1, 3)
    assert created['value'] == 3


def test_points_delete(api_client):
    metrics = cachet.Metrics(api_client)
    metrics.points.delete(1, 1)
    return True


def test_subscribers_list(api_client):
    subscribers = cachet.Subscribers(api_client)
    subscribers_list = list(subscribers.get())
    assert len(subscribers_list) == 2


def test_subscribers_list_paginated(api_client):
    subscribers = cachet.Subscribers(api_client)
    subscribers_list = list(subscribers.get(per_page=1))
    assert len(subscribers_list) == 2


def test_subscribers_create(api_client):
    subscribers = cachet.Subscribers(api_client)
    created = subscribers.create("jacquie@merci.com")
    assert created['email'] == "jacquie@merci.com"


def test_subscribers_delete(api_client):
    subscribers = cachet.Subscribers(api_client)
    subscribers.delete(1)
    return True


def test_actions_enpoint(api_client):
    cachet.Actions(api_client)
    return True


if __name__ == "__main__":

    # Initialise real API for compatibility tests
    c_client = client.CachetAPIClient(**CFG)
    components = cachet.Components(c_client)
    incidents = cachet.Incidents(c_client)
    metrics = cachet.Metrics(c_client)
    subscribers = cachet.Subscribers(c_client)
    actions = cachet.Actions(c_client)

    # Test Component groups on real API
    print("%d component groups" % len(list(components.groups.get())))
    print("%d component groups (paginated)" % len(list(components.groups.get(per_page=1))))
    created = components.groups.create("test component group")
    print("created component group: %d %s" % (created['id'], created['name']))
    compo = list(components.groups.get(created['id']))[0]
    print("get component group: %d %s" % (compo['id'], compo['name']))
    updated = components.groups.update(created['id'], "updated component group")
    print("updated component group: %d %s" % (updated['id'], updated['name']))
    components.groups.delete(created['id'])
    print("deleted component group %d" % created['id'])

    # Test Components on real API
    print("%d components" % len(list(components.get())))
    print("%d components (paginated)" % len(list(components.get(per_page=1))))
    created = components.create("test component", 1)
    print("created component: %d %s" % (created['id'], created['name']))
    compo = list(components.get(created['id']))[0]
    print("get component: %d %s" % (compo['id'], compo['name']))
    updated = components.update(created['id'], "updated component")
    print("updated component: %d %s" % (updated['id'], updated['name']))
    components.delete(created['id'])
    print("deleted component %d" % created['id'])

    # Test Incidents on real API
    print("%d incidents" % len(list(incidents.get())))
    print("%d incidents (paginated)" % len(list(incidents.get(per_page=1))))
    created = incidents.create("test incident", "Test description", 0, 1)
    print("created incident: %d %s" % (created['id'], created['name']))
    compo = list(incidents.get(created['id']))[0]
    print("get incident: %d %s" % (compo['id'], compo['name']))
    updated = incidents.update(created['id'], "updated incident")
    print("updated incident: %d %s" % (updated['id'], updated['name']))
    incidents.delete(created['id'])
    print("deleted incident %d" % created['id'])

    # Test Metrics & points on real API
    created = metrics.create("test metric", "unit", "Test description", 0)
    print("created metric: %d %s" % (created['id'], created['name']))
    print("%d metrics" % len(list(metrics.get())))
    print("%d metrics (paginated)" % len(list(metrics.get(per_page=1))))
    metric = list(metrics.get(created['id']))[0]
    print("get metric: %d %s" % (metric['id'], metric))

    pointA = metrics.points.create(created['id'], 3)
    print("created metric pointA: %d %s" % (metric['id'], pointA))
    pointB = metrics.points.create(created['id'], 4)
    print("created metric pointB: %d %s" % (metric['id'], pointB))
    points = list(metrics.points.get(metric['id']))
    print("metric %d points: %s" % (metric['id'], points))
    metrics.points.delete(created['id'], points[0]['id'])
    print("deleted points %d, %d" % (points[0]['id'], points[0]['id']))
    metrics.delete(created['id'])
    print("deleted metric %d" % created['id'])

    # Test Subscribers on real API
    created_1 = subscribers.create("jacquie@merci.com")
    created_2 = subscribers.create("michel@merci.com")
    print("created subscriber: %d %s" % (created_1['id'], created_1['email']))
    print("created subscriber: %d %s" % (created_2['id'], created_2['email']))
    print("%d subscribers" % len(list(subscribers.get())))
    print("%d subscribers (paginated)" % len(list(subscribers.get(per_page=1))))
    subscribers.delete(created_1['id'])
    subscribers.delete(created_2['id'])
    print("deleted subscribers %d & %d" % (created_1['id'], created_2['id']))