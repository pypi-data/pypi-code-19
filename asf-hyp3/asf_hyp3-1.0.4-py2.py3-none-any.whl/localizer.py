import json
import os
from . import __file__ as module_file


class Hyp3ApiMessages(object):
    def __init__(self):
        self.messages = json.loads(
            open(os.path.join(os.path.dirname(module_file), 'messages.json')).read())

    def error_with_message(self, message):
        return self.messages['general']['error_with_message'] + message

    def error_without_message(self):
        return self.messages['general']['error_without_message']

    def internal_server_error(self, message):
        return self.messages['general']['internal_server_error'].format(message)

    def connection_error(self, url):
        return self.messages['__init__']['connection_error'].format(url)

    def member_is_none(self, arg):
        return self.messages['__init__']['member_is_none'].format(arg)

    def username_exception(self, username):
        return self.messages['login']['username_exception'].format(username)

    def password_prompt(self, username):
        return self.messages['login']['no_password'].format(username)

    def login_successful(self):
        return self.messages['login']['login_success']

    def csv_not_supported_with_selction_on_id(self):
        return self.messages['get_jobs']['csv_not_supported_with_selction_on_id']

    def invalid_granule(self, granule):
        return self.messages['one_time_process']['invalid_granule'].format(granule)

    def granule_pair_required(self):
        return self.messages['one_time_process']['granule_pair_required']

    def dual_pol_granule_required(self):
        return self.messages['one_time_process']['dual_pol_granule_required']

    def shapefile_exception(self, error):
        return self.messages['create_subscription']['shapefile_exception'] + error

    def bad_credentials(self):
        return self.messages['EarthdataLogin']['bad_username_or_password']

    def cookie_error(self):
        return self.messages['EarthdataLogin']['cookie_error']

    def urs_error(self):
        return self.messages['EarthdataLogin']['urs_error']
