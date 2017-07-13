# This class was generated on Thu, 06 Jul 2017 16:03:30 PDT by version 0.01 of Braintree SDK Generator
# payment_get_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"payment.get","Description":"Shows details for a payment, by ID, that has yet to complete. For example, shows details for a payment that was created, approved, or failed.","Parameters":[{"Type":"string","VariableName":"payment_id","Description":"The ID of the payment for which to show details.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null,"Location":"path"}],"RequestType":null,"ResponseType":{"Type":"Payment","VariableName":"","Description":"A payment. Use this object to create, process, and manage payments.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"GET","Path":"/v1/payments/payment/{payment_id}","ExpectedStatusCode":200}



class PaymentGetRequest:
    """
    Shows details for a payment, by ID, that has yet to complete. For example, shows details for a payment that was created, approved, or failed.
    """

    def __init__(self, payment_id):
        self.verb = "GET"
        self.path = "/v1/payments/payment/{payment_id}?".replace("{payment_id}", str(payment_id))
        self.headers = {}

    
