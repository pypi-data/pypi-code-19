"""
Wargaming OpenId backend:
"""
from social.backends.open_id import OpenIdAuth
from social.exceptions import AuthFailed, AuthMissingParameter

USER_INFO = 'https://api.worldoftanks.ru/wot/account/info/?'


class WGnetOpenId(OpenIdAuth):
    name = 'wgnet'
    URL = 'https://ru.wargaming.net/id/openid/yadis'
    AUTH_URL = 'https://api.worldoftanks.ru/wot/auth/login/?application_id={api_key}'
    # EXTRA_DATA = [('access_token','access_token')]

    def user_data(self, *args, **kwargs):
        print 'User Data called'
        super(WGnetOpenId, self).user_data(*args, **kwargs)

    # def openid_url(self):
    #     return self.AUTH_URL.format(api_key=self.setting('SOCIAL_AUTH_WGNET_API_KEY'))

    def get_user_id(self, details, response):
        """Return user unique id provided by service"""
        return self._user_id(response)

    def get_user_details(self, response):
        account_id = self._user_id(response)
        request = self.get_json(USER_INFO, params={
            'application_id': self.setting('SOCIAL_AUTH_WGNET_API_KEY'),
            'account_id': account_id,
        })

        if 'status' in request and request['status'] == 'ok':
            try:
                player_data = request['data'][account_id]
                details = {'username': player_data.get('nickname'),
                            'id': account_id,
                            'email': '',
                            'fullname': '',
                            'first_name': '',
                            'last_name': '',
                            'player': player_data}
            except KeyError:
                details = {}

        return details

    def _user_id(self, response):
        user_id = response.identity_url.rstrip('/').split('/')[-1].split('-')[0]
        if not user_id.isdigit():
            raise AuthFailed(self, 'Missing WG Player Id')
        return user_id

