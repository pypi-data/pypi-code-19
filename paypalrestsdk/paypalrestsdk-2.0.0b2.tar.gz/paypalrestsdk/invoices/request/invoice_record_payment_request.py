# This class was generated on Tue, 18 Jul 2017 12:56:42 PDT by version 0.01 of Braintree SDK Generator
# invoice_record_payment_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"invoice.record-payment","Description":"Marks the status of an invoice, by ID, as paid. Include a payment detail object that defines the payment method and other details in the JSON request body.","Parameters":[{"Type":"string","VariableName":"invoice_id","Description":"The ID of the invoice to mark as paid.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null,"Location":"path"}],"RequestType":{"Type":"Payment Detail","VariableName":"body","Description":"Payment details.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ResponseType":null,"ContentType":"application/json","HttpMethod":"POST","Path":"/v1/invoicing/invoices/{invoice_id}/record-payment","ExpectedStatusCode":200}



class InvoiceRecordPaymentRequest:
    """
    Marks the status of an invoice, by ID, as paid. Include a payment detail object that defines the payment method and other details in the JSON request body.
    """

    def __init__(self, invoice_id):
        self.verb = "POST"
        self.path = "/v1/invoicing/invoices/{invoice_id}/record-payment?".replace("{invoice_id}", str(invoice_id))
        self.headers = {}
        self.headers["Content-Type"] = "application/json"

    
    
    def requestBody(self, body):
        self.body = body
        return self
