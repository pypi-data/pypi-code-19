# coding=utf-8

import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.conf import settings

from all_page_login.middleware import LoginRequiredMiddleware, prepare_urls


@pytest.fixture()
def no_redirect_response():
  return HttpResponse()


@pytest.fixture()
def middleware(no_redirect_response):
  return LoginRequiredMiddleware(get_response=lambda *args: no_redirect_response)


def make_request(path: str, user):
  request = HttpRequest()
  request.path_info = request.path = path
  request.user = user
  return request


def assert_response_is_redirect(response, settings):
  assert response.status_code == 302
  assert response['Location'].startswith(settings.LOGIN_URL)


def assert_response_is_not_redirect(response, no_redirect_response):
  assert response is no_redirect_response

EXEMPT_EXAMPLES = [
  settings.LOGIN_URL,
  "/exempt/foo/",
  "/exempt/bar/",
  "/foo/",
  "exempt/foo/",
  "exempt/bar/",
  "foo/",
]

NOT_EXEMPT_URLS = [
  "/foo",
  "/bar",
  "foo",
  "bar",
]


@pytest.mark.parametrize("exempt_url", EXEMPT_EXAMPLES)
def test_anonymous_user_not_redirect_on_exempt_urls(exempt_url, middleware, no_redirect_response):
  request = make_request(exempt_url, AnonymousUser())
  response = middleware(request)
  assert_response_is_not_redirect(response, no_redirect_response)


@pytest.mark.parametrize("url", NOT_EXEMPT_URLS)
def test_anonymous_user_redirect_on_notexempt_urls(url, middleware, settings):
  request = make_request(url, AnonymousUser())
  response = middleware(request)
  assert_response_is_redirect(response, settings)


@pytest.mark.parametrize("exempt_url", EXEMPT_EXAMPLES)
def test_not_active_user_not_redirect_on_exempt_urls(
    exempt_url,
    middleware,
    no_redirect_response,
    django_user_model
):
  request = make_request(exempt_url, django_user_model(is_active=False))
  response = middleware(request)
  assert_response_is_not_redirect(response, no_redirect_response)


@pytest.mark.parametrize("url", NOT_EXEMPT_URLS)
def test_not_active_user_redirect_on_not_exempt_urls(
    url,
    middleware,
    settings,
    django_user_model
):
  request = make_request(url, django_user_model(is_active=False))
  response = middleware(request)
  assert_response_is_redirect(response, settings)


@pytest.mark.parametrize("url", EXEMPT_EXAMPLES + NOT_EXEMPT_URLS)
def test_active_user_is_never_redireced(
    url,
    middleware,
    no_redirect_response,
    django_user_model
):
  request = make_request(url, django_user_model(is_active=True))
  response = middleware(request)
  assert_response_is_not_redirect(response, no_redirect_response)


def test_missing_user(middleware):

  with pytest.raises(AssertionError):
    middleware(HttpRequest())
  with pytest.raises(AssertionError):
    middleware(make_request("/foo", None))


def test_prepare_urls(settings):
  settings.LOGIN_EXEMPT_URLS = ['/foo']
  with pytest.raises(ImproperlyConfigured):
    prepare_urls()
