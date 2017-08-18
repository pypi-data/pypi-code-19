from __future__ import absolute_import

import pytest
import webtest

from bottle import Bottle, request

from odinweb import bottle
from odinweb.constants import Method, Type
from odinweb.data_structures import PathParam
from odinweb.testing import check_request_proxy


def test_request_proxy():
    test_app = Bottle(catchall=False)
    app = webtest.TestApp(test_app)

    @test_app.route('/')
    def test_method():
        target = bottle.RequestProxy(request)
        check_request_proxy(target)
        assert target.method == Method.GET
        return 'OK'

    assert app.get('/?a=1&b=2&a=3', expect_errors=False).body == 'OK'


@pytest.mark.parametrize('path_node, expected', (
    (PathParam('foo'), "<foo:int>"),
    (PathParam('foo', Type.String), "<foo:re:[-\w.~,!%]+>"),
    (PathParam('foo', Type.Boolean), "<foo:bool>"),
    (PathParam('foo', None), "<foo>"),
))
def test_node_formatter(path_node, expected):
    actual = bottle.Api.node_formatter(path_node)
    assert actual == expected


class TestApi(object):
    def test_merge_api_and_request(self):
        test_app = Bottle(catchall=False)
        app = webtest.TestApp(test_app)
        target = bottle.Api()

        @target.operation('{foo:String}')
        def sample_operation(request, foo):
            assert isinstance(request, bottle.RequestProxy)
            assert foo == 'eek'
            return 'OK'

        test_app.merge(target)

        assert app.get('/api/eek', expect_errors=False).body == '"OK"'
