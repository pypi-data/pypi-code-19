# This class was generated on Thu, 06 Jul 2017 16:03:30 PDT by version 0.01 of Braintree SDK Generator
# capture_refund_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"capture.refund","Description":"Refunds a captured payment, by ID. In the JSON request body, include an `amount` object.","Parameters":[{"Type":"string","VariableName":"capture_id","Description":"The ID of the captured payment to refund.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null,"Location":"path"}],"RequestType":{"Type":"Refund Request","VariableName":"body","Description":"A refund request.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ResponseType":{"Type":"Detailed Refund","VariableName":"","Description":"A refund transaction that is returned by `GET /refund`.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"POST","Path":"/v1/payments/capture/{capture_id}/refund","ExpectedStatusCode":200}



class CaptureRefundRequest:
    """
    Refunds a captured payment, by ID. In the JSON request body, include an `amount` object.
    """

    def __init__(self, capture_id):
        self.verb = "POST"
        self.path = "/v1/payments/capture/{capture_id}/refund?".replace("{capture_id}", str(capture_id))
        self.headers = {}

    
    
    def body(self, body):
        self.body = body
        self.headers["Content-Type"] = "application/json"
