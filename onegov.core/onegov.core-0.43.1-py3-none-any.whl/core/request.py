import collections
import morepath

from cached_property import cached_property
from datetime import timedelta
from functools import lru_cache
from itsdangerous import (
    BadSignature,
    SignatureExpired,
    TimestampSigner,
    URLSafeSerializer,
    URLSafeTimedSerializer
)
from more.webassets.core import IncludeRequest
from morepath.authentication import NO_IDENTITY
from onegov.core import utils
from onegov.core.crypto import random_token
from webob.exc import HTTPForbidden
from wtforms.csrf.session import SessionCSRF


Message = collections.namedtuple('Message', ['text', 'type'])


class ReturnToMixin(object):
    """ Provides a safe and convenient way of using return-to links.

    Return-to links are links with an added 'return-to' query parameter
    which points to the url a specific view (usually with a form) should
    return to, once all is said and done.

    There's no magic involved. If a view should honor the return-to
    paramter, it should use request.redirect instead of morepath.redirect.

    If no return-to parameter was specified, rqeuest.redirect is a
    transparent proxy to morepath.redirect.

    To create a link::

        url = request.return_to(original_url, redirect)

    To honor the paramter in a view, if present::

        return request.redirect(default_url)

    *Do not use the return-to parameter directly*. Redirect parameters
    are notorious for being used in phising attacks. By using ``return_to``
    and ``redirect`` you are kept safe from these attacks as the redirect
    url is signed and verified.

    For the same reason you should not allow the user-data for return-to
    links. Those are meant for internally generated links!

    """

    @property
    def identity_secret(self):
        raise NotImplementedError

    @property
    def redirect_signer(self):
        return URLSafeSerializer(self.identity_secret, 'return-to')

    @lru_cache(maxsize=16)
    def sign_url_for_redirect(self, url):
        return self.redirect_signer.dumps(url)

    def return_to(self, url, redirect):
        signed = self.sign_url_for_redirect(redirect)
        return utils.append_query_param(url, 'return-to', signed)

    def return_here(self, url):
        return self.return_to(url, self.url)

    def redirect(self, url):
        if 'return-to' in self.GET:
            try:
                url = self.redirect_signer.loads(self.GET['return-to'])
            except BadSignature:
                pass

        return morepath.redirect(url)


class CoreRequest(IncludeRequest, ReturnToMixin):
    """ Extends the default Morepath request with virtual host support and
    other useful methods.

    Virtual hosting might be supported by Morepath directly in the future:
    https://github.com/morepath/morepath/issues/185

    """

    @cached_property
    def identity_secret(self):
        return self.app.identity_secret

    def link_prefix(self, *args, **kwargs):
        """ Override the `link_prefix` with the application base path provided
        by onegov.server, because the default link_prefix contains the
        hostname, which is not useful in our case - we'll add the hostname
        ourselves later.

        """
        return getattr(self.app, 'application_base_path', '')

    @cached_property
    def x_vhm_host(self):
        """ Return the X_VHM_HOST variable or an empty string.

        X_VHM_HOST acts like a prefix to all links generated by Morepath.
        If this variable is not empty, it will be added in front of all
        generated urls.
        """
        return self.headers.get('X_VHM_HOST', '').rstrip('/')

    @cached_property
    def x_vhm_root(self):
        """ Return the X_VHM_ROOT variable or an empty string.

        X_VHM_ROOT is a bit more tricky than X_VHM_HOST. It tells Morepath
        where the root of the application is situated. This means that the
        value of X_VHM_ROOT must be an existing path inside of Morepath.

        We can understand this best with an example. Let's say you have a
        Morepath application that serves a blog under /blog. You now want to
        serve the blog under a separate domain, say blog.example.org.

        If we just served Morepath under blog.example.org, we'd get urls like
        this one::

            blog.example.org/blog/posts/2014-11-17-16:00

        In effect, this subdomain would be no different from example.org
        (without the blog subdomain). However, we want the root of the host to
        point to /blog.

        To do this we set X_VHM_ROOT to /blog. Morepath will then automatically
        return urls like this::

            blog.example.org/posts/2014-11-17-16:00

        """
        return self.headers.get('X_VHM_ROOT', '').rstrip('/')

    @cached_property
    def url(self):
        """ Returns the current url, taking the virtual hosting in account. """
        url = self.transform(self.path)

        if self.query_string:
            url += '?' + self.query_string

        return url

    def transform(self, url):
        """ Applies X_VHM_HOST and X_VHM_ROOT to the given url (which is
        expected to not contain a host yet!). """
        if self.x_vhm_root:
            url = '/' + utils.lchop(url, self.x_vhm_root).lstrip('/')

        if self.x_vhm_host:
            url = self.x_vhm_host + url
        else:
            url = self.host_url + url

        return url

    def link(self, *args, **kwargs):
        """ Extends the default link generating function of Morepath. """
        return self.transform(super().link(*args, **kwargs))

    def class_link(self, *args, **kwargs):
        """ Extends the default class link generating function of Morepath. """
        return self.transform(super().class_link(*args, **kwargs))

    def filestorage_link(self, path):
        """ Takes the given filestorage path and returns an url if the path
        exists. The url might point to the local server or it might point to
        somehwere else on the web.

        """

        app = self.app

        if not app.filestorage.exists(path):
            return None

        if app.filestorage.hasurl(path):
            url = app.filestorage.geturl(path)

            if not url.startswith('file://'):
                return url

        return self.link(app.modules.filestorage.FilestorageFile(path))

    @cached_property
    def theme_link(self):
        """ Returns the link to the current theme. Computed once per request.

        The theme is automatically compiled and stored if it doesn't exist yet,
        or if it is outdated.

        """
        theme = self.app.settings.core.theme
        assert theme is not None, "Do not call if no theme is used"

        force = self.app.always_compile_theme or (
            self.app.allow_shift_f5_compile and
            self.headers.get('cache-control') == 'no-cache' and
            self.headers.get('x-requested-with') != 'XMLHttpRequest')

        filename = self.app.modules.theme.compile(
            self.app.themestorage, theme, self.app.theme_options,
            force=force
        )

        return self.link(self.app.modules.theme.ThemeFile(filename))

    @cached_property
    def browser_session(self):
        """ Returns a browser_session bound to the request. Works via cookies,
        so requests without cookies won't be able to use the browser_session.

        The browser session is bound to the application (by id), so no session
        data is shared between the applications.

        If no data is written to the browser_session, no session_id cookie
        is created.

        """

        if 'session_id' in self.cookies:
            session_id = self.app.unsign(self.cookies['session_id'])
            session_id = session_id or random_token()
        else:
            session_id = random_token()

        def on_dirty(namespace, token):
            self.cookies['session_id'] = self.app.sign(token)

            @self.after
            def store_session(response):
                response.set_cookie(
                    'session_id',
                    self.cookies['session_id'],
                    secure=self.app.identity_secure,
                    httponly=True
                )

        return self.app.modules.browser_session.BrowserSession(
            namespace=self.app.application_id,
            token=session_id,
            cache=self.app.session_cache,
            on_dirty=on_dirty
        )

    def get_form(self, form_class, i18n_support=True, csrf_support=True,
                 data=None, model=None):
        """ Returns an instance of the given form class, set up with the
        correct translator and with CSRF protection enabled (the latter
        doesn't work yet).

        Form classes passed to this function (or defined through the
        ``App.form`` directive) may define a ``on_request`` method, which
        is called after the request has been bound to the form and before
        the view function is called.

        """
        meta = {}

        if i18n_support:
            translate = self.get_translate(for_chameleon=False)
            form_class = self.app.modules.i18n.get_translation_bound_form(
                form_class, translate)

            meta['locales'] = [self.locale, 'en'] if self.locale else []

        if csrf_support:
            meta['csrf'] = True
            meta['csrf_context'] = self.browser_session
            meta['csrf_class'] = SessionCSRF
            meta['csrf_secret'] = self.app.csrf_secret.encode('utf-8')
            meta['csrf_time_limit'] = timedelta(
                seconds=self.app.csrf_time_limit)

        form = form_class(self.POST, meta=meta, data=data)

        assert not hasattr(form, 'request')
        form.request = self
        form.model = model

        if hasattr(form, 'on_request'):
            form.on_request()

        return form

    def translate(self, text):
        """ Transalates the given text, if it's a translatable text. """

        if not hasattr(text, 'domain'):
            return text

        return self.translator(text)

    @cached_property
    def translator(self):
        """ Returns the translate function for basic string translations. """
        translator = self.get_translate()
        if translator:
            return lambda text: text.interpolate(translator.gettext(text))

        return lambda text: text.interpolate(text)

    @cached_property
    def default_locale(self):
        """ Returns the default locale. """
        return self.app.settings.i18n.default_locale

    @cached_property
    def locale(self):
        """ Returns the current locale of this request. """
        settings = self.app.settings

        locale = settings.i18n.locale_negotiator(self.app.locales, self)

        return locale or settings.i18n.default_locale

    @cached_property
    def html_lang(self):
        """ The language code for the html tag. """
        return self.locale and self.locale.replace('_', '-') or ''

    def get_translate(self, for_chameleon=False):
        """ Returns the translate method to the given request, or None
        if no such method is availabe.

        :for_chameleon:
            True if the translate instance is used for chameleon (which is
            special).

        """

        if not self.app.locales:
            return None

        if for_chameleon:
            return self.app.chameleon_translations.get(self.locale)
        else:
            return self.app.translations.get(self.locale)

    def message(self, text, type):
        """ Adds a message with the given type to the messages list. This
        messages list may then be displayed by an applicaiton building on
        onegov.core.

        For example:

            http://foundation.zurb.com/docs/components/alert_boxes.html

        Four default types are defined on the request for easier use:

        :meth:`success`
        :meth:`warning`
        :meth:`info`
        :meth:`alert`

        The messages are stored with the session and to display them, the
        template using the messages should call :meth:`consume_messages`.

        """
        if not self.browser_session.has('messages'):
            self.browser_session.messages = [Message(text, type)]
        else:
            # this is a bit akward, but I don't see an easy way for this atm.
            # (otoh, usually there's going to be one message only)
            self.browser_session.messages = self.browser_session.messages + [
                Message(text, type)
            ]

    def consume_messages(self):
        """ Returns the messages, removing them from the session in the
        process. Call only if you can be reasonably sure that the user
        will see the messages.

        """
        if self.browser_session.has('messages'):
            yield from self.browser_session.messages
            del self.browser_session.messages

    def success(self, text):
        """ Adds a success message. """
        self.message(text, 'success')

    def warning(self, text):
        """ Adds a warning message. """
        self.message(text, 'warning')

    def info(self, text):
        """ Adds an info message. """
        self.message(text, 'info')

    def alert(self, text):
        """ Adds an alert message. """
        self.message(text, 'alert')

    @cached_property
    def is_logged_in(self):
        """ Returns True if the current request is logged in at all. """
        return self.identity is not NO_IDENTITY

    def has_permission(self, model, permission):
        """ Returns True if the current user has the given permission on the
        given model.

        """
        if permission is None:
            return True

        return self.app._permits(self.identity, model, permission)

    def has_access_to_url(self, url):
        """ Returns true if the current user has access to the given url.

        The domain part of the url is completely ignored. This method should
        only be used if you have no other choice. Loading the object by
        url first is slower than if you can get the object otherwise.

        The initial use-case for this function is the to parameter in the
        login view. If the to-url is accessible anyway, we skip the login
        view.

        If we can't find a view for the url, a KeyError is thrown.

        """
        obj, view_name = self.app.object_by_path(url, with_view_name=True)

        if obj is None:
            raise KeyError("Could not find view for '{}'".format(url))

        permission = self.app.permission_by_view(obj, view_name)
        return self.has_permission(obj, permission)

    def exclude_invisible(self, models):
        """ Excludes models invisble to the current user from the list. """
        return [m for m in models if self.is_visible(m)]

    def is_visible(self, model):
        """ Returns True if the given model is visible to the current user.
        This is basically an alias for :meth:`CoreRequest.is_public`. It exists
        because it is easier to understand than ``is_public``.

        """
        return self.has_permission(model, self.app.modules.security.Public)

    def is_public(self, model):
        """ Returns True if the current user has the Public permission for
        the given model.

        """
        return self.has_permission(model, self.app.modules.security.Public)

    def is_private(self, model):
        """ Returns True if the current user has the Private permission for
        the given model.

        """
        return self.has_permission(model, self.app.modules.security.Private)

    def is_secret(self, model):
        """ Returns True if the current user has the Secret permission for
        the given model.

        """
        return self.has_permission(model, self.app.modules.security.Secret)

    @cached_property
    def current_role(self):
        """ Returns the user-role of the current request, if logged in.
        Otherwise, None is returned.

        """
        return self.is_logged_in and self.identity.role or None

    def has_role(self, *roles):
        """ Returns true if the current user has any of the given roles. """

        assert roles and all(roles)
        return self.current_role in roles

    @cached_property
    def csrf_salt(self):
        if not self.browser_session.has('csrf_salt'):
            self.browser_session['csrf_salt'] = random_token()

        return self.browser_session['csrf_salt']

    def new_csrf_token(self, salt=None):
        """ Returns a new CSRF token. A CSRF token can be verified
        using :meth:`is_valid_csrf_token`.

        Note that forms do their own CSRF protection. This is meant
        for CSRF protection outside of forms.

        onegov.core uses the Synchronizer Token Pattern for CSRF protection:
        `<https://www.owasp.org/index.php/\
        Cross-Site_Request_Forgery_%28CSRF%29_Prevention_Cheat_Sheet>`_

        New CSRF tokens are signed usign a secret attached to the session (but
        not sent out to the user). Clients have to return the CSRF token they
        are given. The token has to match the secret, which the client doesn't
        know. So an attacker would have to get access to both the cookie and
        the html source to be able to forge a request.

        Since cookies are marked as HTTP only (no javascript access), this
        even prevents CSRF attack combined with XSS.

        """
        # no csrf tokens for anonymous users (there's not really a point
        # to doing this)
        if not self.is_logged_in:
            return ''

        assert salt or self.csrf_salt
        salt = salt or self.csrf_salt

        # use app.identity_secret here, because that's being used for
        # more.itsdangerous, which uses the same algorithm
        signer = TimestampSigner(self.identity_secret, salt=salt)

        return signer.sign(random_token())

    def assert_valid_csrf_token(self, signed_value=None, salt=None):
        """ Validates the given CSRF token and returns if it was
        created by :meth:`new_csrf_token`. If there's a mismatch, a 403 is
        raised.

        If no signed_value is passed, it is taken from
        request.params.get('csrf-token').

        """
        signed_value = signed_value or self.params.get('csrf-token')
        salt = salt or self.csrf_salt

        if not signed_value:
            raise HTTPForbidden()

        if not salt:
            raise HTTPForbidden()

        signer = TimestampSigner(self.identity_secret, salt=salt)
        try:
            signer.unsign(signed_value, max_age=self.app.csrf_time_limit)
        except (SignatureExpired, BadSignature):
            raise HTTPForbidden()

    def new_url_safe_token(self, data, salt=None):
        """ Returns a new URL safe token. A token can be deserialized
        using :meth:`load_url_safe_token`.

        """
        serializer = URLSafeTimedSerializer(self.identity_secret)
        return serializer.dumps(data, salt=salt)

    def load_url_safe_token(self, data, salt=None, max_age=3600):
        """ Deserialize a token created by :meth:`new_url_safe_token`.

        If the token is invalid, None is returned.

        """
        serializer = URLSafeTimedSerializer(self.identity_secret)
        try:
            return serializer.loads(data, salt=salt, max_age=max_age)
        except (SignatureExpired, BadSignature):
            return None
