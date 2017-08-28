"""
Auth0 (https://auth0.com/) enables authentication
of users using different system.

Currently only social login and traditional DB
with user-password are used.

The Authentication system is traditional web application
is as follows:
- A lock object (JavaScript) makes a request to the Auth0 server.
- The servers responds to an URL specified in the lock object with
   a code that identifies the user
- The Authentication tool must use this code to authenticate the
  user in the Auth0 servers, which respond with the user information

As of December 2016, the users were logged in right after
signing in. Moreover, email verification was not required
as email were send using the Auth0 service which should not
be used for development.
"""


import json
import urllib
import cherrypy
import requests
import http.client
from functools import partial

from bgweb.bgprofile.auth0_profile import Auth0Profile
from .authentication import AuthenticationTool, AuthError, TokenAuthentication, TokenNotFoundError, UserNotFoundError


class Auth0Error(AuthError):

    def __init__(self, message, status=None, reason=None):
        self.message = message
        self.status = status
        self.reason = reason


class Auth0(AuthenticationTool):

    def __init__(self, configuration, login_path, logout_path, force_login_function, user_id_str='user_id', user_profile_str='user_profile', login_redirect=None, logout_redirect=None):
        """
        This tool is intended to intercept all requests to the server and check if the request
        is done to one of the login or logout paths or to a page/resource that is protected.

        Args:
            configuration (dict): must be compliant with auth0.confspec
            login_path (str): path to be intercepted for the log in
            logout_path (str): path to be intercepted for the log in
            force_login_function (func): function to be called if the login is required
            user_id_str (str): string that is used in the session as key of the value corresponding to the user ID
            login_redirect (str): URL to redirect after the user logs out via HTTPRedirect (default to None).
            logout_redirect (str): URL to redirect after the user logs out via HTTPRedirect (default to None).

        In order to emulate the reload of the page after log in done with Mozilla persona,
        the tool expects to receive the URL to redirect from the state parameter of the lock object.
        In this implementation it is done using the window.location.href

        Limitations are:
        - authentication_user_information is used in the cherrypy session to
            store additional information from the user
        - If you want the page reload after log in feature to work, the force login
          function should retrieve the code for the page without changing the URL.
          E.g.: give a function that does something like:
          return self.env.get_template('login.html').render
        """
        self.conf = configuration
        auth_func = partial(self.authenticate, login_path=login_path, logout_path=logout_path)
        super(Auth0, self).__init__(auth_func.func, force_login_function, user_id_str)
        self.login_redirect = login_redirect
        self.logout_redirect = logout_redirect
        self.user_profile_str = user_profile_str
        if self.user_profile_str is None:
            self.get_user_profile = lambda: None
        else:
            self.get_user_profile = lambda: cherrypy.session.get(self.user_profile_str, None)

    def authenticate(self, login_path='/authenticate', logout_path='/logout', require=None):
        """
        Entry point for this tool.
        Intercepts the URL matching login_path or logout_path and changes the handlers.
        Additionally, checks if the request resource is under *authentication.require*

        Args:
            login_path (str): path to be intercepted when logging in
            logout_path (str): path to be intercepted when logging out
            require (str): this parameter is given for the static content with the
               authentication.require

        """
        if cherrypy.request.path_info == login_path:
            cherrypy.request.handler = self.authentication_callback
            return
        elif cherrypy.request.path_info == logout_path:
            cherrypy.request.handler = self.logout
            return

        if require is not None and not self.get_user():
            raise cherrypy.HTTPRedirect(require.format(cherrypy.request.path_info))

        conditions = cherrypy.request.config.get('authentication.require', None)

        if conditions is not None:

            if not self.get_user():
                # the user is not logged in, but the tool is enabled, so instead
                #  of allowing the default handler to run, respond instead with
                #  the authentication page.
                cherrypy.request.handler = self.force_login
            else:

                for condition in conditions:
                    # A condition is just a callable that returns true or false
                    if not condition():
                        cherrypy.request.handler = self.force_login


    def authentication_callback(self):
        """
        Handler for log-ins.

        Raises
            HTTPError if authentication fails

        The redirect URL is expected from the state parameter of the Auth0 Lock.

        """
        code = cherrypy.request.params.get('code', None)
        redirect_url = cherrypy.request.params.get('state', None)

        error = cherrypy.request.params.get('error', None)
        error_description = cherrypy.request.params.get('error_description', None)

        if error is not None:
            raise cherrypy.HTTPError(500, "Invalid. Error when connecting with Auth0. {} : {}".format(error, error_description))

        json_header = {'content-type': 'application/json'}

        token_url = "https://{domain}/oauth/token".format(domain=self.conf['AUTH0_DOMAIN'])

        token_payload = {
            'client_id': self.conf['AUTH0_CLIENT_ID'],
            'client_secret': self.conf['AUTH0_CLIENT_SECRET'],
            'redirect_uri': self.conf['AUTH0_CALLBACK_URL'],
            'code': code,
            'grant_type': 'authorization_code'
        }

        token_info = requests.post(token_url, data=json.dumps(token_payload), headers=json_header).json()

        user_url = "https://{domain}/userinfo?access_token={access_token}".format(
            domain=self.conf['AUTH0_DOMAIN'],
            access_token=token_info['access_token'])

        user_info = requests.get(user_url).json()

        # We're saving all user information into the session
        self.login_user(user_info.get('email'))

        if self.user_profile_str is not None:
            user_info['token_id'] = token_info['id_token']
            cherrypy.session[self.user_profile_str] = Auth0Profile(self.get_user(), user_info, self.conf['AUTH0_DOMAIN'])

        if self.login_redirect is not None:
            raise cherrypy.HTTPRedirect(self.login_redirect)
        elif redirect_url is not None:
            raise cherrypy.HTTPRedirect(redirect_url)


    def logout(self):
        """
        Handler for log-outs.

        """
        cherrypy.response.headers['Cache-Control'] = 'no-cache'

        self.logout_user()

        if self.user_profile_str in cherrypy.session:
            del cherrypy.session[self.user_profile_str]

        if self.logout_redirect is not None:
            raise cherrypy.HTTPRedirect(self.logout_redirect)

    def get_static_javascript(self):
        """

        Returns:
            str. Javascript static content for the Auth0 lock

        This JS code uses the 'window.location.href' to get the URL of the
        current page and to know where to redirect

        """
        external = '<script src="https://cdn.auth0.com/js/lock/10.4/lock.min.js"></script>'

        lock_options = (
            '{'
                'auth: '
                '{ redirectUrl: "'
                +self.conf['AUTH0_CALLBACK_URL']+
                '",'
                'responseType: "code",'
                'responseMode: "form_post",'
                'params: { '
                    'scope: "openid email",'
                    'state: window.location.href'
                    '}'
                '}'
            '}'
        )

        lock = (
            '<script>'
                'var lock = new Auth0Lock("'
                    +self.conf['AUTH0_CLIENT_ID']+
                    '","'
                    +self.conf['AUTH0_DOMAIN']+
                    '",'
                    +lock_options+
                ');'
            '</script>'
        )

        return '\n'.join([external, lock])


class Auth0Token(TokenAuthentication):

    def __init__(self, domain, client, secret):

        self.domain = domain
        self.client = client
        self.secret = secret

        self.__connect()

        self.retried = False  # flag to avoid possible infinite loops


    def __connect(self):
        conn = http.client.HTTPSConnection(self.domain)

        payload = {'client_id': self.client,'client_secret': self.secret, 'audience': 'https://'+self.domain+'/api/v2/','grant_type':'client_credentials'}
        payload = json.dumps(payload)

        headers = {'content-type': "application/json"}

        conn.request("POST", "/oauth/token", payload, headers)

        res = conn.getresponse()

        data = res.read()

        data = data.decode("utf-8")

        conn.close()

        if res.status < 400:
            data = json.loads(data)
            self.token = data['access_token']
            self.token_type = data['token_type']
        else:
            raise Auth0Error(data, res.status, res.reason)

    def check_token(self, user_id, token):

        conn = http.client.HTTPSConnection(self.domain)

        headers = {'authorization': ' '.join([self.token_type, self.token])}

        parameter = urllib.parse.quote('email:"{}"'.format(user_id))
        conn.request("GET", "/api/v2/users?q={}".format(parameter), headers=headers)

        res = conn.getresponse()
        data = res.read()

        data = data.decode("utf-8")

        conn.close()

        print(res.status, res.msg)

        if res.status < 400:
            self.retried = False
            data = json.loads(data)
            for user_data in data:
                user_email = user_data.get('email', None)
                if user_email == user_id:
                    try:
                        user_token = user_data['user_metadata']['api_token']
                    except KeyError:
                        raise TokenNotFoundError()
                    break # only 1 user is expected
            else:
                raise UserNotFoundError()
            return token == user_token
        else:
            # It is possible to get an error here if the token expires (last for 1 day)
            # When that happens, we try to connect again to Auth0 to ask for a new token and do the check again
            if self.retried:
                raise Auth0Error(data, res.status, res.reason)
            else:
                self.retried = True
                self.__connect()
                return self.check_token(user_id, token)
