# This class was generated on Tue, 18 Jul 2017 12:56:42 PDT by version 0.01 of Braintree SDK Generator
# template_create_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"template.create","Description":"Creates a template.","Parameters":[],"RequestType":{"Type":"Template","VariableName":"body","Description":"Invoicing template.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ResponseType":{"Type":"Template","VariableName":"","Description":"Invoicing template.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"POST","Path":"/v1/invoicing/templates","ExpectedStatusCode":200}



class TemplateCreateRequest:
    """
    Creates a template.
    """

    def __init__(self):
        self.verb = "POST"
        self.path = "/v1/invoicing/templates?"
        self.headers = {}
        self.headers["Content-Type"] = "application/json"

    
    
    def requestBody(self, body):
        self.body = body
        return self
