# This class was generated on Thu, 06 Jul 2017 16:03:30 PDT by version 0.01 of Braintree SDK Generator
# authorization_get_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"authorization.get","Description":"Shows details for an authorization, by ID.","Parameters":[{"Type":"string","VariableName":"authorization_id","Description":"The ID of the authorization for which to show details.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null,"Location":"path"}],"RequestType":null,"ResponseType":{"Type":"Authorization","VariableName":"","Description":"An authorization.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"GET","Path":"/v1/payments/authorization/{authorization_id}","ExpectedStatusCode":200}



class AuthorizationGetRequest:
    """
    Shows details for an authorization, by ID.
    """

    def __init__(self, authorization_id):
        self.verb = "GET"
        self.path = "/v1/payments/authorization/{authorization_id}?".replace("{authorization_id}", str(authorization_id))
        self.headers = {}

    
