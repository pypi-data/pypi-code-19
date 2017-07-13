# This class was generated on Thu, 06 Jul 2017 16:03:37 PDT by version 0.01 of Braintree SDK Generator
# invoice_next_invoice_number_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"invoice.next_invoice_number","Description":"Generates the next invoice number that is available to the merchant.","Parameters":[],"RequestType":null,"ResponseType":{"Type":"Invoice number","VariableName":"","Description":"","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"POST","Path":"/v1/invoicing/invoices/next-invoice-number","ExpectedStatusCode":200}



class InvoiceNextInvoiceNumberRequest:
    """
    Generates the next invoice number that is available to the merchant.
    """

    def __init__(self):
        self.verb = "POST"
        self.path = "/v1/invoicing/invoices/next-invoice-number?"
        self.headers = {}

    
