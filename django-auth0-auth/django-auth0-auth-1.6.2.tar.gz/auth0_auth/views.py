from .backends import Auth0Backend
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, resolve_url
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
import logging
from urlparse import urlparse
import uuid


logger = logging.getLogger('auth0_auth')


@never_cache
def auth(request):
    backend = Auth0Backend()
    redirect_uri = request.build_absolute_uri(reverse(callback))
    state = str(uuid.uuid4())
    request.session['state'] = state
    logger.info('auth view: session state - {}'.format(state))
    login_url = backend.login_url(
        redirect_uri=redirect_uri,
        state=state,
    )
    logger.info('auth view: login url - {}'.format(login_url))
    return HttpResponseRedirect(login_url)


@never_cache
def logout(request):
    backend = Auth0Backend()
    redirect_uri = request.build_absolute_uri(resolve_url(settings.LOGOUT_URL))
    logout_url = backend.logout_url(
        redirect_uri=redirect_uri,
    )
    return HttpResponseRedirect(logout_url)


@never_cache
@csrf_exempt
def callback(request):
    backend = Auth0Backend()
    original_state = request.session.get('state')
    logger.info('callback view: session state - {}'.format(original_state))
    state = request.POST.get('state')
    logger.info('callback view: request state - {}'.format(state))
    if original_state == state:
        token = request.POST.get('id_token')
        logger.info('callback view: token - {}'.format(token))
        user = backend.authenticate(token=token)
        logger.info('callback view: user - {}'.format(user))
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(get_login_success_url(request))
    return redirect('auth0_login')


def get_login_success_url(request):
    redirect_to = request.GET.get(REDIRECT_FIELD_NAME, '')
    netloc = urlparse(redirect_to)[1]
    if not redirect_to:
        redirect_to = settings.LOGIN_REDIRECT_URL
    elif netloc and netloc != request.get_host():
        redirect_to = settings.LOGIN_REDIRECT_URL
    return redirect_to
