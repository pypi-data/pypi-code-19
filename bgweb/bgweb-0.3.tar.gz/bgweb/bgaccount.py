import os
import cherrypy
from os.path import isdir, join

from bgweb.tools.authentication import AuthListener


class AccountFactory(object):

    @staticmethod
    def create(account_class):

        persona_id = cherrypy.session['username'] if 'username' in cherrypy.session else None
        userdata_base_dir = cherrypy.request.app.config['userdata']['dir']

        if 'user_account' not in cherrypy.session:
            cherrypy.session['user_account'] = account_class(persona_id, userdata_base_dir)

        return cherrypy.session['user_account']


class BGAccount(object):

    def __init__(self, persona_id=None, userdata_dir_base=None):

        self._persona_id = persona_id

        # user account
        if persona_id is None:
            self._persona_id = 'exampledata'

        # Data dir of user
        assert isdir(userdata_dir_base)
        self._userdata_dir = join(userdata_dir_base, self._persona_id)
        self.create_user_dir(userdata_dir_base)

    @staticmethod
    def create_user_dir(userdata_dir):
        try:
            assert isdir(userdata_dir)
        except AssertionError:
            os.mkdir(userdata_dir)


class BGaccountPersonaListener(AuthListener):

    def __init__(self, account_class):
        self.account_class = account_class

    def login(self):
        persona_id = cherrypy.session['username'] if 'username' in cherrypy.session else None
        userdata_base_dir = cherrypy.request.app.config['userdata']['dir']
        cherrypy.session['user_account'] = self.account_class(persona_id, userdata_base_dir)

    def logout(self):
        userdata_base_dir = cherrypy.request.app.config['userdata']['dir']
        cherrypy.session['user_account'] = self.account_class(None, userdata_base_dir)


class LogUsers(AuthListener):
    """
    Keep track of user that log into our page.

    :param registered_file: file where to store the users email address

    Users are identified by their email address (lowercase).
    """

    def __init__(self, registered_file):
        self.register_file = registered_file
        if os.path.isfile(registered_file):
            self.registered_users = [u.strip().lower() for u in open(registered_file)]
        else:
            open(registered_file, 'a').close()
            self.registered_users = []

    def login(self):
        """
        When a users logs in he/she is registered (if that username wasn't).
        """
        username = cherrypy.session['username']
        if username not in self.registered_users:
            self.__register_user(username)

    def __register_user(self, user_name):
        """
        Updates the file with all users

        :param user_name: email address of the user
        :type user_name: str
        """
        with open(self.register_file, 'at') as fd:
            fd.write(user_name + '\n')
        self.registered_users.append(user_name)