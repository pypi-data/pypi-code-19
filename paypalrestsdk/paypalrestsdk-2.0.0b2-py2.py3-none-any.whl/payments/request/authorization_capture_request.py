# This class was generated on Mon, 31 Jul 2017 18:51:41 UTC by version 0.1 of Braintree SDK Generator
# authorization_capture_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"authorization.capture","Description":"Captures and processes an authorization, by ID. To use this call, the original payment call must specify an intent of `authorize`.\u003cbr/\u003e\u003cbr/\u003eA successful request returns the HTTP `201 Created` status code and a JSON response body that shows details for the captured authorization.","QueryParameters":[],"HeaderParameters":[],"FormParameters":[],"PathParameters":[{"Type":"string","VariableName":"authorization_id","Description":"The ID of the authorization to capture.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null}],"RequestType":{"Type":"Capture","VariableName":"body","Description":"A capture transaction.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ResponseType":{"Type":"Capture","VariableName":"","Description":"A capture transaction.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"POST","Path":"/v1/payments/authorization/{authorization_id}/capture","ExpectedStatusCode":200}



class AuthorizationCaptureRequest:
    """
    Captures and processes an authorization, by ID. To use this call, the original payment call must specify an intent of `authorize`.<br/><br/>A successful request returns the HTTP `201 Created` status code and a JSON response body that shows details for the captured authorization.
    """

    def __init__(self, authorization_id):
        self.verb = "POST"
        self.path = "/v1/payments/authorization/{authorization_id}/capture?".replace("{authorization_id}", str(authorization_id))
        self.headers = {}
        self.headers["Content-Type"] = "application/json"
        self.body = {}

    
    
    def requestBody(self, body):
        self.body = body
        return self
