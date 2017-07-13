# This class was generated on Thu, 06 Jul 2017 16:03:37 PDT by version 0.01 of Braintree SDK Generator
# template_get_templates_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"template.get_templates","Description":"Lists all merchant-created templates. The list shows the emails, addresses, and phone numbers from the merchant profile.","Parameters":[{"Type":"string","VariableName":"fields","Description":"The fields to return in the response. Value is `all` or `none`. Specify `none` to return only the template name, ID, and default attributes.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null,"Location":"query"}],"RequestType":null,"ResponseType":{"Type":"Templates","VariableName":"","Description":"List of merchant templates.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"GET","Path":"/v1/invoicing/templates/","ExpectedStatusCode":200}



class TemplateGetTemplatesRequest:
    """
    Lists all merchant-created templates. The list shows the emails, addresses, and phone numbers from the merchant profile.
    """

    def __init__(self):
        self.verb = "GET"
        self.path = "/v1/invoicing/templates/?"
        self.headers = {}

    def fields(self, fields):
        self.path += self.path + "fields=" + str(fields) + "&"
        return self

    
