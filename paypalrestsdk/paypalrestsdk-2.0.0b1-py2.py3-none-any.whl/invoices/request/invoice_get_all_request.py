# This class was generated on Thu, 06 Jul 2017 16:03:37 PDT by version 0.01 of Braintree SDK Generator
# invoice_get_all_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"invoice.get_all","Description":"Lists merchant invoices. To filter the invoices that appear in the response, you can specify one or more optional query parameters.","Parameters":[{"Type":"integer","VariableName":"page","Description":"A *zero-relative* index of the list of merchant invoices.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null,"Location":"query"},{"Type":"integer","VariableName":"page_size","Description":"The number of invoices to list beginning with the specified `page`.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null,"Location":"query"},{"Type":"boolean","VariableName":"total_count_required","Description":"Indicates whether the total count appears in the response. Default is `false`.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null,"Location":"query"}],"RequestType":null,"ResponseType":{"Type":"Invoices","VariableName":"","Description":"List of merchant invoices. Can include the total invoices count and HATEOAS links for navigation.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"GET","Path":"/v1/invoicing/invoices/","ExpectedStatusCode":200}



class InvoiceGetAllRequest:
    """
    Lists merchant invoices. To filter the invoices that appear in the response, you can specify one or more optional query parameters.
    """

    def __init__(self):
        self.verb = "GET"
        self.path = "/v1/invoicing/invoices/?"
        self.headers = {}

    def page(self, page):
        self.path += self.path + "page=" + str(page) + "&"
        return self

    def pageSize(self, pageSize):
        self.path += self.path + "page_size=" + str(pageSize) + "&"
        return self

    def totalCountRequired(self, totalCountRequired):
        self.path += self.path + "total_count_required=" + str(totalCountRequired) + "&"
        return self

    
