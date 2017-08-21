from utils.service import Service  

class BanregioApiHelper(Service):

    def __init__(self,access_token,base_uri=None):
        Service.__init__(self,access_token,base_uri)


    def get_accounts(self):
        
        response = self._build_http_request("v1/accounts/",'get')
        return response.json()

    def get_transactions(self,id,**kwargs):

        response = self._build_http_request(
            "v1/accounts/{id}/transactions".format(id=id),
            'get',
            **kwargs
        )
        return response.json()

    def get_enterprise_transactions(self,id,**kwargs):

        response = self._build_http_request(
            "v1/accounts/{id}/transactions".format(id=id),
            'get',
            **kwargs
        )
        return response.json()






