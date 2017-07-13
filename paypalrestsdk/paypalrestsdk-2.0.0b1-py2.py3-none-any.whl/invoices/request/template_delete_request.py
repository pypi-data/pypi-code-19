# This class was generated on Thu, 06 Jul 2017 16:03:37 PDT by version 0.01 of Braintree SDK Generator
# template_delete_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"template.delete","Description":"Deletes a template, by ID.","Parameters":[{"Type":"string","VariableName":"template_id","Description":"The ID of the template to delete.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null,"Location":"path"}],"RequestType":null,"ResponseType":null,"ContentType":"application/json","HttpMethod":"DELETE","Path":"/v1/invoicing/templates/{template_id}","ExpectedStatusCode":200}



class TemplateDeleteRequest:
    """
    Deletes a template, by ID.
    """

    def __init__(self, template_id):
        self.verb = "DELETE"
        self.path = "/v1/invoicing/templates/{template_id}?".replace("{template_id}", str(template_id))
        self.headers = {}

    
