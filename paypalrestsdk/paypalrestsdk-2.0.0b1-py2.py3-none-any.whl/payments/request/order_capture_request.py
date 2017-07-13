# This class was generated on Thu, 06 Jul 2017 16:03:30 PDT by version 0.01 of Braintree SDK Generator
# order_capture_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"order.capture","Description":"Captures a payment for an order, by ID. To use this call, the original payment call must specify an `order` intent. In the JSON request body, include the payment amount and indicate whether this capture is the final capture for the authorization.","Parameters":[{"Type":"string","VariableName":"order_id","Description":"The ID of the order to capture.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null,"Location":"path"}],"RequestType":{"Type":"Capture","VariableName":"body","Description":"A capture transaction.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ResponseType":{"Type":"Capture","VariableName":"","Description":"A capture transaction.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"POST","Path":"/v1/payments/orders/{order_id}/capture","ExpectedStatusCode":200}



class OrderCaptureRequest:
    """
    Captures a payment for an order, by ID. To use this call, the original payment call must specify an `order` intent. In the JSON request body, include the payment amount and indicate whether this capture is the final capture for the authorization.
    """

    def __init__(self, order_id):
        self.verb = "POST"
        self.path = "/v1/payments/orders/{order_id}/capture?".replace("{order_id}", str(order_id))
        self.headers = {}

    
    
    def body(self, body):
        self.body = body
        self.headers["Content-Type"] = "application/json"
