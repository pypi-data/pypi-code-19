# This class was generated on Thu, 06 Jul 2017 16:03:30 PDT by version 0.01 of Braintree SDK Generator
# payment_update_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"payment.update","Description":"Partially updates a payment, by ID. You can update the amount, shipping address, invoice ID, and custom data. You cannot update a payment after the payment executes.","Parameters":[{"Type":"string","VariableName":"payment_id","Description":"The ID of the payment to update.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null,"Location":"path"}],"RequestType":{"Type":"JSON Patch","VariableName":"body","Description":"A JSON patch request.","IsArray":true,"ReadOnly":false,"Required":false,"Properties":null},"ResponseType":null,"ContentType":"application/json","HttpMethod":"PATCH","Path":"/v1/payments/payment/{payment_id}","ExpectedStatusCode":200}



class PaymentUpdateRequest:
    """
    Partially updates a payment, by ID. You can update the amount, shipping address, invoice ID, and custom data. You cannot update a payment after the payment executes.
    """

    def __init__(self, payment_id):
        self.verb = "PATCH"
        self.path = "/v1/payments/payment/{payment_id}?".replace("{payment_id}", str(payment_id))
        self.headers = {}

    
    
    def body(self, body):
        self.body = body
        self.headers["Content-Type"] = "application/json"
