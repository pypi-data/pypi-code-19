# This class was generated on Thu, 06 Jul 2017 16:03:30 PDT by version 0.01 of Braintree SDK Generator
# refund_get_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"refund.get","Description":"Shows details for a refund, by ID.","Parameters":[{"Type":"string","VariableName":"refund_id","Description":"The ID of the refund for which to show details.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null,"Location":"path"}],"RequestType":null,"ResponseType":{"Type":"Refund","VariableName":"","Description":"A refund transaction.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"GET","Path":"/v1/payments/refund/{refund_id}","ExpectedStatusCode":200}



class RefundGetRequest:
    """
    Shows details for a refund, by ID.
    """

    def __init__(self, refund_id):
        self.verb = "GET"
        self.path = "/v1/payments/refund/{refund_id}?".replace("{refund_id}", str(refund_id))
        self.headers = {}

    
