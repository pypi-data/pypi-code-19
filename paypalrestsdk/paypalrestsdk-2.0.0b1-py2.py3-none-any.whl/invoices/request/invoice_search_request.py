# This class was generated on Thu, 06 Jul 2017 16:03:37 PDT by version 0.01 of Braintree SDK Generator
# invoice_search_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"invoice.search","Description":"Lists invoices that match search criteria. In the JSON request body, include a `search` object that specifies the search criteria.","Parameters":[],"RequestType":{"Type":"Search","VariableName":"body","Description":"Invoice search parameters.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ResponseType":{"Type":"Invoices","VariableName":"","Description":"List of merchant invoices. Can include the total invoices count and HATEOAS links for navigation.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"POST","Path":"/v1/invoicing/search","ExpectedStatusCode":200}



class InvoiceSearchRequest:
    """
    Lists invoices that match search criteria. In the JSON request body, include a `search` object that specifies the search criteria.
    """

    def __init__(self):
        self.verb = "POST"
        self.path = "/v1/invoicing/search?"
        self.headers = {}

    
    
    def body(self, body):
        self.body = body
        self.headers["Content-Type"] = "application/json"
