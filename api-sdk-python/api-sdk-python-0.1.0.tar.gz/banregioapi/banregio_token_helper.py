from rauth import OAuth2Service

# Errors
PROCESS_TOKEN_ERROR = "Error to handle the request, provider response with: {raw}"
PROCESS_REFRESH_TOKEN_ERROR = "Refresh token is not present. You are sure to get the get_access_token() method successfully first?"

class BanregioTokenHelper():

    def __init__(self,client_id,secret_key,redirect_uri=None,base_uri='https://api.banregio.com'):
        self.redirect_uri = redirect_uri
        self.base_uri = base_uri
        self.refresh_token = None
        self.api = OAuth2Service(
            client_id=client_id,
            client_secret=secret_key,
            name='apibanregio',
            authorize_url='{0}/oauth/authorize'.format(self.base_uri),
            access_token_url='{0}/oauth/token'.format(self.base_uri),
            base_url=self.base_uri
        )

    def get_authorize_url(self):
        params = {
          'response_type': 'code',
          'redirect_uri': self.redirect_uri
        }
        return self.api.get_authorize_url(**params)

    def get_access_token(self,code):

        response = self._build_raw_access_token_request(code=code)

        try:

            self.refresh_token = response.json()['refresh_token']
            self.access_token = response.json()['access_token']
            return self.access_token

        except KeyError as e:
            raise KeyError(PROCESS_TOKEN_ERROR.format(raw=response.content))

    def get_refresh_token(self):

        if self.refresh_token:
            return self.refresh_token
        else:
            raise StandardError(PROCESS_REFRESH_TOKEN_ERROR)

    def get_access_token_with_client_credentials(self):

        response = self._build_raw_access_token_request(grant_type='client_credentials')

        try:

            self.access_token = response.json()['access_token']
            return self.access_token

        except KeyError as e:
            raise KeyError(PROCESS_TOKEN_ERROR.format(raw=response.content))
        except Exception as e:
            print e.message    


    def get_access_token_with_refresh_token(self,refresh_token):
        response = self._build_raw_access_token_request(
                grant_type = 'refresh_token',
                refresh_token=refresh_token
                )
        try:

            self.refresh_token = response.json()['refresh_token']
            self.access_token = response.json()['access_token']
            return self.access_token

        except KeyError as e:
            self.refresh_token = None
            raise KeyError(PROCESS_TOKEN_ERROR.format(raw=response.content))


    def _build_raw_access_token_request(self,grant_type='authorization_code',code=None,refresh_token=None):

        data = {}

        if code and grant_type == 'authorization_code':
            data['code'] = code
            data['grant_type'] = grant_type
            data['redirect_uri'] = self.redirect_uri
    
        if refresh_token and grant_type == 'refresh_token':
            data['refresh_token'] = refresh_token
            data['grant_type'] = grant_type

        if grant_type == 'client_credentials':
            data['grant_type'] = grant_type    

        return self.api.get_raw_access_token(data=data)  


            

