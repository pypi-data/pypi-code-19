# This class was generated on Mon, 31 Jul 2017 18:51:41 UTC by version 0.1 of Braintree SDK Generator
# order_authorize_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"order.authorize","Description":"Authorizes an order, by ID. In the JSON request body, include an `amount` object.\u003cbr/\u003e\u003cbr/\u003eA successful request returns the HTTP `201 Created` status code and a JSON response body that shows details for the authorized order.","QueryParameters":[],"HeaderParameters":[],"FormParameters":[],"PathParameters":[{"Type":"string","VariableName":"order_id","Description":"The ID of the order to authorize.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null}],"RequestType":{"Type":"Order","VariableName":"body","Description":"An order transaction.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ResponseType":{"Type":"Authorization","VariableName":"","Description":"An authorization.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"POST","Path":"/v1/payments/orders/{order_id}/authorize","ExpectedStatusCode":200}



class OrderAuthorizeRequest:
    """
    Authorizes an order, by ID. In the JSON request body, include an `amount` object.<br/><br/>A successful request returns the HTTP `201 Created` status code and a JSON response body that shows details for the authorized order.
    """

    def __init__(self, order_id):
        self.verb = "POST"
        self.path = "/v1/payments/orders/{order_id}/authorize?".replace("{order_id}", str(order_id))
        self.headers = {}
        self.headers["Content-Type"] = "application/json"
        self.body = {}

    
    
    def requestBody(self, body):
        self.body = body
        return self
