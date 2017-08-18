# This class was generated on Mon, 31 Jul 2017 18:51:41 UTC by version 0.1 of Braintree SDK Generator
# order_void_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"order.void","Description":"Voids, or cancels, an order, by ID. You cannot void an order if the payment has already been partially or fully captured.\u003cbr/\u003e\u003cbr/\u003eA successful request returns the HTTP `200 OK` status code and a JSON response body that shows details for the voided order.","QueryParameters":[],"HeaderParameters":[],"FormParameters":[],"PathParameters":[{"Type":"string","VariableName":"order_id","Description":"The ID of the order to void.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null}],"RequestType":null,"ResponseType":{"Type":"Order","VariableName":"","Description":"An order transaction.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"POST","Path":"/v1/payments/orders/{order_id}/do-void","ExpectedStatusCode":200}



class OrderVoidRequest:
    """
    Voids, or cancels, an order, by ID. You cannot void an order if the payment has already been partially or fully captured.<br/><br/>A successful request returns the HTTP `200 OK` status code and a JSON response body that shows details for the voided order.
    """

    def __init__(self, order_id):
        self.verb = "POST"
        self.path = "/v1/payments/orders/{order_id}/do-void?".replace("{order_id}", str(order_id))
        self.headers = {}
        self.headers["Content-Type"] = "application/json"
        self.body = {}

    
