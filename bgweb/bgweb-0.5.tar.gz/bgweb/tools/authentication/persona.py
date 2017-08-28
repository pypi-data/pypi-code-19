"""
Mozilla Persona is a tool for authentication:
https://developer.mozilla.org/en-US/Persona

You register with your email address, and it
authenticates you for each domain.
"""

import os
import cherrypy
import browserid
from functools import partial

from .authentication import AuthenticationTool


class Persona(AuthenticationTool):

    def __init__(self, configuration, login_path, logout_path, force_login_function, user_id_str='user_id', login_redirect = None, logout_redirect = None):
        """
        This tool is intended to intercept all requests to the server and check if the request
        is done to one of the login or logout paths or to a page/resource that is protected.

        Args:
            configuration (dict): must me compliant with persona.confspec
            login_path (str): path to be intercepted for the log in
            logout_path (str): path to be intercepted for the log out
            force_login_function (func): function to be called if the login is required
            user_id_str (str): string that is used in the session as key of the value corresponding to the user ID
            login_redirect (str): URL to redirect the user after a log in via HTTPRedirect (default to None).
               As the implementation works reloading the page it is not required.
            logout_redirect (str): URL to redirect after the user logs out via HTTPRedirect (default to None).
               As the implementation works reloading the page it is not required.

        This implementation works with Ajax
        and reloads the page after logging in or out
        using: window.location.reload().
        If you want a different behaviour, you can generate your
        own JS code.

        The limitations of this implementation are:
        - do not use the variable persona_authentication_user_id in your JavaScript code
        - dynamic JS code is required to generate the above mentioned variable
        - as it is working with Ajax, once the force login is called, this function should retrieve the
          code for the page without changing the URL. E.g.: give a function that does something like:
          return self.env.get_template('login.html').render
        """
        self.conf = configuration
        auth_func = partial(self.authenticate, login_path=login_path, logout_path=logout_path)
        super(Persona, self).__init__(auth_func.func, force_login_function, user_id_str)
        self.login_redirect = login_redirect
        self.logout_redirect = logout_redirect



    def authenticate(self, login_path='/login', logout_path='/logout', require=None):
        """
        Entry point for this tool.
        Intercepts the URL matching login_path or logout_path and changes the handlers.
        Additionally, checks if the request resource is under *authentication.require*

        Args:
            login_path (str): path to be intercepted when logging in
            logout_path (str): path to be intercepted when logging out
            require (str): this parameter is given for the static content with the
               authentication.require

        Audience is the host name and port on which this server is hosting.
        It may be set to 'HOST' to use the HOST header, but this setting
        SHOULD ONLY BE USED when the HOST header has been verified by a
        trusted party (such as a reverse-proxy).
        """
        if cherrypy.request.path_info == login_path:
            cherrypy.request.handler = self.login
            return
        elif cherrypy.request.path_info == logout_path:
            cherrypy.request.handler = self.logout
            return

        if require is not None and not self.get_user():
            raise cherrypy.HTTPRedirect(require.format(cherrypy.request.path_info))

        conditions = cherrypy.request.config.get('authentication.require', None)

        if conditions is not None:

            if self.conf['audience'] == 'HOST':
                self.conf['audience'] = cherrypy.request.headers['HOST']

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


    def login(self):
        """
        Handler for log-ins.

        Raises
            HTTPError if authentication fails
        """
        cherrypy.response.headers['Cache-Control'] = 'no-cache'

        assertion = cherrypy.request.params['assertion']
        # Verify the assertion using browserid.
        validation = browserid.verify(assertion, self.conf['audience'])

        # Check if the assertion was valid
        if validation['status'] != 'okay':
            raise cherrypy.HTTPError(400, "invalid")

        # Log the user in
        self.login_user(validation['email'])

        return 'You are logged in'

    def logout(self):
        """
        Handler for log-outs.

        """
        cherrypy.response.headers['Cache-Control'] = 'no-cache'

        self.logout_user()

        if self.logout_redirect is not None:
            raise cherrypy.HTTPRedirect(self.logout_redirect)
        return 'You are logged out'


    def get_static_javascript(self):
        """

        Returns:
            str. Static JS code that can be used by the web app.

        """
        # Static content
        external = '<script src="https://login.persona.org/include.js"></script>'

        persona_js = '<script>'
        dir = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(dir, 'javascripts', 'persona.js')
        with open(file) as fd:
            persona_js += fd.read()
        persona_js += '</script>'

        return '\n'.join([external, persona_js])

    def get_dynamic_javascript(self):
        """
        Set the persona_authentication_user_id variable
        if the user is logged in.

        Returns:
            str. Dynamic JS code

        """
        # Dynamic content content
        user = self.get_user()
        if user is None:
            return ''
        else:
            script = ('var persona_authentication_user_id = "'
                      +user+
                      '\";')

            return script
