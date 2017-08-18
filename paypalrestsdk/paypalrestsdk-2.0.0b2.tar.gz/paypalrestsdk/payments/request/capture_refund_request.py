# This class was generated on Mon, 31 Jul 2017 18:51:41 UTC by version 0.1 of Braintree SDK Generator
# capture_refund_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"capture.refund","Description":"Refunds a captured payment, by ID. In the JSON request body, include an `amount` object.\u003cbr/\u003e\u003cbr/\u003eA successful request returns the HTTP `200 OK` status code and a JSON response body that shows details for the captured payment.","QueryParameters":[],"HeaderParameters":[],"FormParameters":[],"PathParameters":[{"Type":"string","VariableName":"capture_id","Description":"The ID of the captured payment to refund.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null}],"RequestType":{"Type":"Refund Request","VariableName":"body","Description":"A refund request.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ResponseType":{"Type":"Detailed Refund","VariableName":"","Description":"A refund transaction that is returned by `GET /refund`.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"POST","Path":"/v1/payments/capture/{capture_id}/refund","ExpectedStatusCode":200}



class CaptureRefundRequest:
    """
    Refunds a captured payment, by ID. In the JSON request body, include an `amount` object.<br/><br/>A successful request returns the HTTP `200 OK` status code and a JSON response body that shows details for the captured payment.
    """

    def __init__(self, capture_id):
        self.verb = "POST"
        self.path = "/v1/payments/capture/{capture_id}/refund?".replace("{capture_id}", str(capture_id))
        self.headers = {}
        self.headers["Content-Type"] = "application/json"
        self.body = {}

    
    
    def requestBody(self, body):
        self.body = body
        return self
