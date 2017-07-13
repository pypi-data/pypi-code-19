# This class was generated on Thu, 06 Jul 2017 16:03:37 PDT by version 0.01 of Braintree SDK Generator
# invoice_update_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"invoice.update","Description":"Fully updates an invoice, by ID. In the JSON request body, include a complete `invoice` object. This call does not support partial updates.","Parameters":[{"Type":"string","VariableName":"invoice_id","Description":"The ID of the invoice to update.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null,"Location":"path"},{"Type":"boolean","VariableName":"notify_merchant","Description":"Indicates whether to send the invoice update notification to the merchant. Default is `true`.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null,"Location":"query"}],"RequestType":{"Type":"Invoice","VariableName":"body","Description":"Invoice details.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ResponseType":{"Type":"Invoice","VariableName":"","Description":"Invoice details.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"PUT","Path":"/v1/invoicing/invoices/{invoice_id}","ExpectedStatusCode":200}



class InvoiceUpdateRequest:
    """
    Fully updates an invoice, by ID. In the JSON request body, include a complete `invoice` object. This call does not support partial updates.
    """

    def __init__(self, invoice_id):
        self.verb = "PUT"
        self.path = "/v1/invoicing/invoices/{invoice_id}?".replace("{invoice_id}", str(invoice_id))
        self.headers = {}

    def notifyMerchant(self, notifyMerchant):
        self.path += self.path + "notify_merchant=" + str(notifyMerchant) + "&"
        return self

    
    
    def body(self, body):
        self.body = body
        self.headers["Content-Type"] = "application/json"
