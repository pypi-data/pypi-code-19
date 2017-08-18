# This class was generated on Mon, 31 Jul 2017 18:51:41 UTC by version 0.1 of Braintree SDK Generator
# refund_get_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"refund.get","Description":"Shows details for a refund, by ID.\u003cbr/\u003e\u003cbr/\u003eA successful request returns the HTTP `200 OK` status code and a JSON response body that shows refund details.","QueryParameters":[],"HeaderParameters":[],"FormParameters":[],"PathParameters":[{"Type":"string","VariableName":"refund_id","Description":"The ID of the refund for which to show details.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null}],"RequestType":null,"ResponseType":{"Type":"Refund","VariableName":"","Description":"A refund transaction.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"GET","Path":"/v1/payments/refund/{refund_id}","ExpectedStatusCode":200}



class RefundGetRequest:
    """
    Shows details for a refund, by ID.<br/><br/>A successful request returns the HTTP `200 OK` status code and a JSON response body that shows refund details.
    """

    def __init__(self, refund_id):
        self.verb = "GET"
        self.path = "/v1/payments/refund/{refund_id}?".replace("{refund_id}", str(refund_id))
        self.headers = {}
        self.headers["Content-Type"] = "application/json"
        self.body = {}

    
