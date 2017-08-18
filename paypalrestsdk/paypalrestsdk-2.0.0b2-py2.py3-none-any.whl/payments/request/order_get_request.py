# This class was generated on Mon, 31 Jul 2017 18:51:41 UTC by version 0.1 of Braintree SDK Generator
# order_get_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"order.get","Description":"Shows details for an order, by ID.\u003cbr/\u003e\u003cbr/\u003eA successful request returns the HTTP `200 OK` status code and a JSON response body that shows details for the voided authorization.","QueryParameters":[],"HeaderParameters":[],"FormParameters":[],"PathParameters":[{"Type":"string","VariableName":"order_id","Description":"The ID of the order for which to show details.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null}],"RequestType":null,"ResponseType":{"Type":"Order","VariableName":"","Description":"An order transaction.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"GET","Path":"/v1/payments/orders/{order_id}","ExpectedStatusCode":200}



class OrderGetRequest:
    """
    Shows details for an order, by ID.<br/><br/>A successful request returns the HTTP `200 OK` status code and a JSON response body that shows details for the voided authorization.
    """

    def __init__(self, order_id):
        self.verb = "GET"
        self.path = "/v1/payments/orders/{order_id}?".replace("{order_id}", str(order_id))
        self.headers = {}
        self.headers["Content-Type"] = "application/json"
        self.body = {}

    
