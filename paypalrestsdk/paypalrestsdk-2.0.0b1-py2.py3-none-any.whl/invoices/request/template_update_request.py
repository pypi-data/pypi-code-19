# This class was generated on Thu, 06 Jul 2017 16:03:37 PDT by version 0.01 of Braintree SDK Generator
# template_update_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"template.update","Description":"Updates a template, by ID. In the JSON request body, specify a complete `template` object. The update method does not support partial updates.","Parameters":[{"Type":"string","VariableName":"template_id","Description":"The ID of the template to update.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null,"Location":"path"}],"RequestType":{"Type":"Template","VariableName":"body","Description":"Invoicing template.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ResponseType":{"Type":"Template","VariableName":"","Description":"Invoicing template.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"PUT","Path":"/v1/invoicing/templates/{template_id}","ExpectedStatusCode":200}



class TemplateUpdateRequest:
    """
    Updates a template, by ID. In the JSON request body, specify a complete `template` object. The update method does not support partial updates.
    """

    def __init__(self, template_id):
        self.verb = "PUT"
        self.path = "/v1/invoicing/templates/{template_id}?".replace("{template_id}", str(template_id))
        self.headers = {}

    
    
    def body(self, body):
        self.body = body
        self.headers["Content-Type"] = "application/json"
