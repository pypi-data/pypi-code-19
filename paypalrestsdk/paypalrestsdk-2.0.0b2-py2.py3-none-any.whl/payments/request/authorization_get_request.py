# This class was generated on Mon, 31 Jul 2017 18:51:41 UTC by version 0.1 of Braintree SDK Generator
# authorization_get_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"authorization.get","Description":"Shows details for an authorization, by ID.\u003cbr/\u003e\u003cbr/\u003eA successful request returns the HTTP `200 OK` status code and a JSON response body that shows authorization details.","QueryParameters":[],"HeaderParameters":[],"FormParameters":[],"PathParameters":[{"Type":"string","VariableName":"authorization_id","Description":"The ID of the authorization for which to show details.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null}],"RequestType":null,"ResponseType":{"Type":"Authorization","VariableName":"","Description":"An authorization.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"GET","Path":"/v1/payments/authorization/{authorization_id}","ExpectedStatusCode":200}



class AuthorizationGetRequest:
    """
    Shows details for an authorization, by ID.<br/><br/>A successful request returns the HTTP `200 OK` status code and a JSON response body that shows authorization details.
    """

    def __init__(self, authorization_id):
        self.verb = "GET"
        self.path = "/v1/payments/authorization/{authorization_id}?".replace("{authorization_id}", str(authorization_id))
        self.headers = {}
        self.headers["Content-Type"] = "application/json"
        self.body = {}

    
