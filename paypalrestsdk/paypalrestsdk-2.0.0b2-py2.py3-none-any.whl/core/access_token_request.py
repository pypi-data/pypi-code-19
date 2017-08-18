class AccessTokenRequest():

    def __init__(self, paypal_environment, refresh_token=None):
        self.path = "/v1/oauth2/token"
        self.verb = "POST"
        self.body = "grant_type=client_credentials"
        if refresh_token:
            self.path = "/v1/identity/openidconnect/tokenservice"
            self.body += "&refresh_token={0}".format(refresh_token)

        self.headers = {}
        self.headers["Content-Type"] = "application/x-www-form-urlencoded"
        self.headers["Authorization"] = paypal_environment.authorization_string()
