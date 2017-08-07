"""Django middleware that forces login"""
import typing
import re

from urllib.parse import urlencode

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect


def prepare_urls():
  """Extracts compiled exempt urls from settings."""
  exempt_urls = [re.compile(settings.LOGIN_URL.lstrip('/'))]
  if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    for expr in settings.LOGIN_EXEMPT_URLS:
      if expr.startswith("/"):
        raise ImproperlyConfigured("LOGIN_EXEPT_URLS can't start with /")
      exempt_urls.append(re.compile(expr))
  return exempt_urls


EXEMPT_URLS = prepare_urls()


class LoginRequiredMiddleware(object):
  """
  Middleware that requires a user to be authenticated to view any page other
  than LOGIN_URL. Exemptions to this requirement can optionally be specified
  in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
  you can copy from your urls.py).

  Requires authentication middleware and template context processors to be
  loaded. You'll get an error if they aren't.
  """

  def __init__(self, get_response=typing.Callable[[], HttpResponse]):
    super().__init__()
    self.get_response = get_response

  def __call__(self, request: HttpRequest):
    assert hasattr(request, 'user'), self.__USER_ASSERT_MSG
    assert getattr(request, 'user', None) is not None, self.__USER_ASSERT_MSG

    user = request.user

    if not (user.is_authenticated and user.is_active):
      path = request.path_info.lstrip('/')
      if not any(m.match(path) for m in EXEMPT_URLS):
        return HttpResponseRedirect(
          "{}?{}".format(
            settings.LOGIN_URL, urlencode(query={"next": request.path})
          )
        )

    return self.get_response(request)

  __USER_ASSERT_MSG = (
    "The Login Required middleware "
    "requires authentication middleware to be installed. Edit your "
    "MIDDLEWARE_CLASSES setting to insert  "
    "'django.contrib.auth.middleware.AuthenticationMiddleware'. If that doesn't "
    "work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes "
    "django.core.context_processors.auth'.")

