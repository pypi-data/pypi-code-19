# This class was generated on Thu, 06 Jul 2017 16:03:37 PDT by version 0.01 of Braintree SDK Generator
# invoice_get_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"invoice.get","Description":"Shows details for an invoice, by ID.","Parameters":[{"Type":"string","VariableName":"invoice_id","Description":"The ID of the invoice for which to show details.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null,"Location":"path"}],"RequestType":null,"ResponseType":{"Type":"Invoice","VariableName":"","Description":"Invoice details.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"GET","Path":"/v1/invoicing/invoices/{invoice_id}","ExpectedStatusCode":200}



class InvoiceGetRequest:
    """
    Shows details for an invoice, by ID.
    """

    def __init__(self, invoice_id):
        self.verb = "GET"
        self.path = "/v1/invoicing/invoices/{invoice_id}?".replace("{invoice_id}", str(invoice_id))
        self.headers = {}

    
