# This class was generated on Mon, 31 Jul 2017 18:51:41 UTC by version 0.1 of Braintree SDK Generator
# capture_get_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"capture.get","Description":"Shows details for a captured payment, by ID.\u003cbr/\u003e\u003cbr/\u003eA successful request returns the HTTP `200 OK` status code and a JSON response body that shows details for the captured payment.","QueryParameters":[],"HeaderParameters":[],"FormParameters":[],"PathParameters":[{"Type":"string","VariableName":"capture_id","Description":"The ID of the captured payment for which to show details.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null}],"RequestType":null,"ResponseType":{"Type":"Capture","VariableName":"","Description":"A capture transaction.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"GET","Path":"/v1/payments/capture/{capture_id}","ExpectedStatusCode":200}



class CaptureGetRequest:
    """
    Shows details for a captured payment, by ID.<br/><br/>A successful request returns the HTTP `200 OK` status code and a JSON response body that shows details for the captured payment.
    """

    def __init__(self, capture_id):
        self.verb = "GET"
        self.path = "/v1/payments/capture/{capture_id}?".replace("{capture_id}", str(capture_id))
        self.headers = {}
        self.headers["Content-Type"] = "application/json"
        self.body = {}

    
