# This class was generated on Mon, 31 Jul 2017 18:51:41 UTC by version 0.1 of Braintree SDK Generator
# payment_update_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"payment.update","Description":"Partially updates a payment, by ID. You can update the amount, shipping address, invoice ID, and custom data. You cannot update a payment after the payment executes.\u003cbr/\u003e\u003cbr/\u003eA successful request returns the HTTP `200 OK` status code and a JSON response body that shows payment details.","QueryParameters":[],"HeaderParameters":[],"FormParameters":[],"PathParameters":[{"Type":"string","VariableName":"payment_id","Description":"The ID of the payment to update.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null}],"RequestType":{"Type":"JSON Patch","VariableName":"body","Description":"A JSON patch request.","IsArray":true,"ReadOnly":false,"Required":false,"Properties":null},"ResponseType":null,"ContentType":"application/json","HttpMethod":"PATCH","Path":"/v1/payments/payment/{payment_id}","ExpectedStatusCode":200}



class PaymentUpdateRequest:
    """
    Partially updates a payment, by ID. You can update the amount, shipping address, invoice ID, and custom data. You cannot update a payment after the payment executes.<br/><br/>A successful request returns the HTTP `200 OK` status code and a JSON response body that shows payment details.
    """

    def __init__(self, payment_id):
        self.verb = "PATCH"
        self.path = "/v1/payments/payment/{payment_id}?".replace("{payment_id}", str(payment_id))
        self.headers = {}
        self.headers["Content-Type"] = "application/json"
        self.body = {}

    
    
    def requestBody(self, body):
        self.body = body
        return self
