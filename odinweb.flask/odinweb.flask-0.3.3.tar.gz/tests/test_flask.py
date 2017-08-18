import pytest

from flask import Flask, request

from odinweb import flask
from odinweb.constants import Method, Type
from odinweb.data_structures import PathParam
from odinweb.testing import check_request_proxy


def test_request_proxy():
    test_app = Flask(__name__)
    test_app.testing = True
    app = test_app.test_client()

    @test_app.route('/')
    def test_method():
        target = flask.RequestProxy(request)
        check_request_proxy(target)
        assert target.method == Method.GET
        return 'OK'

    rv = app.get('/?a=1&b=2&a=3')


class TestApiBlueprint(object):
    @pytest.mark.parametrize('node, expected', (
        (PathParam('foo'), '<int:foo>'),
        (PathParam('bar', Type.String), '<string:bar>'),
        (PathParam('bar', None, None), '<bar>'),
    ))
    def test_node_formatter(self, node, expected):
        actual = flask.ApiBlueprint.node_formatter(node)
        assert actual == expected
