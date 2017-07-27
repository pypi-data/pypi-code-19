import logging

from .command import Command
logger = logging.getLogger(__name__)

DEFAULT_API_HOST = 'api.faaspot.com'


class Profiles(Command):
    def __init__(self, *args, **kwargs):
        self._logger = logger
        super(Profiles, self).__init__(*args, **kwargs)

    def list(self, all=False):
        self.columns = ['name', 'config']
        logger.debug('Going to list profiles..')
        selected_profile = self._config.faaspot.profile
        all_profiles = self._config.faaspot.profiles.todict()
        list_profiles = [{'name': k, 'config': v} for k, v in all_profiles.items()]
        for item in list_profiles:
            name = item['name']
            item['name'] = '*{0}*'.format(name) if name == selected_profile else name
        return list_profiles

    def create(self, name=None, username=None, password=None, token=None, host=None, port=None,
               protocol=None, certificate=None, update_if_exist=False, set_as_active_profile=False):
        logger.debug('Going to create a profile `{0}`'.format(name))
        name = name or 'default'
        if self._profile_exists(name):
            if not update_if_exist:
                raise Exception("Command invalid. Profile `{0}` already exists."
                                "\nUse --update-if-exist if you wish to update it.".format(name))
            return self.update(name,
                               host=host,
                               protocol=protocol,
                               port=port,
                               username=username,
                               password=password,
                               token=token,
                               certificate=certificate)
        profile = self._profile_dict(host=host,
                                     protocol=protocol,
                                     port=port,
                                     username=username,
                                     password=password,
                                     token=token,
                                     certificate=certificate)
        self._config.faaspot.profiles[name] = profile
        if len(self._config.faaspot.profiles) == 1 or set_as_active_profile:
            self._config.faaspot.profile = name
        self._config.save()
        return 'Profile created: {0}'.format(name)

    def update(self, name, username=None, password=None, token=None, host=None, port=None,
               protocol=None, certificate=None):
        try:
            profile_name = name or self._config.faaspot.profile
            logger.debug('Going to update profile `{0}`'.format(profile_name))
            profile = self._get_profile_or_raise(name)
            host = host if host else profile.get('host')
            profile = self._profile_dict(host=host,
                                         protocol=protocol,
                                         port=port,
                                         username=username,
                                         password=password,
                                         token=token,
                                         certificate=certificate,
                                         current=profile)
            self._config.faaspot.profiles[name] = profile
            self._config.save()
            return 'Profile `{0}` updated successfully'.format(name)
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise

    def get(self, name):
        logger.debug('Going to return `{0}` profile info'.format(name))
        profile_name = name
        profile = self._get_profile_or_raise(name)
        return {profile_name: profile}

    def use(self, name, suppress_error=False):
        logger.debug('Going to change current profile to: {0}'.format(name))
        if suppress_error:
            profile = self._get_profile_or_none(name)
            if not profile:
                return 'Requested profile does not exists: {0}'.format(name)
        else:
            profile = self._get_profile_or_raise(name)
        if not suppress_error and not profile.get('token') and \
                not profile.get('username') and not profile.get('password'):
            raise Exception('Can not use profile `{0}`. '
                            'Selected profile must have either '
                            'token or user/pass credentials.'.format(name))
        self._config.faaspot.profile = name
        self._config.save()
        return 'Current profile: {0}'.format(name)

    def current(self):
        logger.debug('Going to return current profile info')
        profile_name = self._config.faaspot.profile
        if not profile_name:
            return None
        profile = self._get_profile_or_raise(profile_name)
        return {profile_name: profile}

    def delete(self, name, suppress_error=False):
        logger.debug('Going to delete profile `{0}`'.format(name))
        if suppress_error:
            if not self._get_profile_or_none(name):
                return 'Profile `{0}` does not exists'.format(name)
        else:
            self._get_profile_or_raise(name)
        del self._config.faaspot.profiles[name]
        if self._config.faaspot.profile == name:
            self._config.faaspot.profile = ''
        self._config.save()
        return "Profile `{0}` deleted".format(name)

    def _get_profile_or_raise(self, name):
        try:
            profile = self._config.faaspot.profiles[name]
        except KeyError:
            raise Exception('Failed retrieving profile `{0}` - '
                            'profile does not exist'.format(name))
        return profile

    def _get_profile_or_none(self, name):
        try:
            profile = self._config.faaspot.profiles[name]
        except KeyError:
            return None
        return profile

    def _profile_exists(self, name):
        try:
            self._config.faaspot.profiles[name]
        except KeyError:
            return False
        return True

    @staticmethod
    def _profile_dict(username=None, password=None, token=None, host=None, port=None,
                      protocol=None, certificate=None, trust_all=None, ssl_enabled=None,
                      current=None):
        if current:
            # We're using ".get" since this parameters might not exists in current profile settings
            host = host or current.get('host')
            username = username or current.get('username')
            password = password or current.get('password')
            token = token or current.get('token')
            port = port or current.get('port')
            certificate = certificate or current.get('ssl_certificate')
            trust_all = trust_all or current.get('ssl_trust_all')
            ssl_enabled = ssl_enabled or current.get('ssl_enabled')
        profile_data = {
            'host': host or DEFAULT_API_HOST,
        }
        if host:
            profile_data['host'] = host
        if protocol:
            profile_data['protocol'] = protocol
        if username:
            profile_data['username'] = username
        if password:
            profile_data['password'] = password
        if token:
            profile_data['token'] = token
        if port:
            profile_data['port'] = port
        if certificate:
            profile_data['ssl_certificate'] = certificate
        if trust_all:
            profile_data['ssl_trust_all'] = trust_all
        if ssl_enabled:
            profile_data['ssl_enabled'] = ssl_enabled
        return profile_data

    @staticmethod
    def _extract_host_info(host):
        if not host:
            return None, None
        if ':' not in host:
            host += ':80'
        return host.split(':')
