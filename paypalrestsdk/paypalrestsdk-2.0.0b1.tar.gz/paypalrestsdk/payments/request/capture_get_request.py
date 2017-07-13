# This class was generated on Thu, 06 Jul 2017 16:03:30 PDT by version 0.01 of Braintree SDK Generator
# capture_get_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"capture.get","Description":"Shows details for a captured payment, by ID.","Parameters":[{"Type":"string","VariableName":"capture_id","Description":"The ID of the captured payment for which to show details.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null,"Location":"path"}],"RequestType":null,"ResponseType":{"Type":"Capture","VariableName":"","Description":"A capture transaction.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"GET","Path":"/v1/payments/capture/{capture_id}","ExpectedStatusCode":200}



class CaptureGetRequest:
    """
    Shows details for a captured payment, by ID.
    """

    def __init__(self, capture_id):
        self.verb = "GET"
        self.path = "/v1/payments/capture/{capture_id}?".replace("{capture_id}", str(capture_id))
        self.headers = {}

    
