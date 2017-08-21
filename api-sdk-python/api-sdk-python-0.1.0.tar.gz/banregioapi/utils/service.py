import requests
import urlparse

from urllib import urlencode

class Service():
    

    def __init__(self,access_token,base_uri=None):
        if base_uri:
            self.base_uri = base_uri
        else:
            self.base_uri = 'https://api.banregio.com'    
        self.access_token = access_token


    def _build_http_request(self,end_point,method,**kwargs):
        
        req = None

        if method == 'get':
            url =  "{base_uri}/{end_point}".format(
                base_uri=self.base_uri,
                end_point=end_point
            )
            
            url = self._update_url_params(url,kwargs)

            req = requests.get(
                url,
                headers=self._set_headers()
            )

        return req

    def _set_headers(self):

        headers = {
            'Authorization': "Bearer {token}".format(token=self.access_token),
            'Content-Type': "application/json"
        }

        return headers

    def _update_url_params(self,url,params):

        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urlencode(query)

        return urlparse.urlunparse(url_parts)  