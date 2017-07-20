# coding=utf-8

from django.test import RequestFactory, SimpleTestCase
from jinja2 import Environment

from dinja2.filters import do_append_get


class AppendToGetTests(SimpleTestCase):
    def test_replace(self):
        path = "/organization/list?page=4&page=5&page=8&page=11"
        path = do_append_get(path, page=55)
        self.assertEqual("/organization/list?page=55", path)

    def test_leave_existing_params(self):
        path = "/search?q=java%2Cpython%2Cdjango"
        path = do_append_get(path, page=55)
        self.assertEqual("/search?q=java%2Cpython%2Cdjango&page=55", path)


class TestActiveUrlExtension(SimpleTestCase):
    def test_render(self):
        env = Environment(extensions=['dinja2.ext.active'])
        tmpl = env.from_string('''\
                {% is_active a %}
                {% is_active b %}
                {% is_active c, 'current' -%}
                ''')
        request = RequestFactory().get("bar")
        body = tmpl.render(a='/foo', b='/bar', c='/bar', request=request)
        self.assertEqual(['', 'active', 'current'], [x.strip() for x in body.splitlines()])
