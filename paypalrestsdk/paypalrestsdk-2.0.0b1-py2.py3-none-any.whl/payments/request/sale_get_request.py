# This class was generated on Thu, 06 Jul 2017 16:03:30 PDT by version 0.01 of Braintree SDK Generator
# sale_get_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"sale.get","Description":"Shows details for a sale, by ID. Returns only sales that were created through the REST API.","Parameters":[{"Type":"string","VariableName":"sale_id","Description":"The ID of the sale for which to show details.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null,"Location":"path"}],"RequestType":null,"ResponseType":{"Type":"Sale","VariableName":"","Description":"A sale transaction. Returned as a part of payment-related resources.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"GET","Path":"/v1/payments/sale/{sale_id}","ExpectedStatusCode":200}



class SaleGetRequest:
    """
    Shows details for a sale, by ID. Returns only sales that were created through the REST API.
    """

    def __init__(self, sale_id):
        self.verb = "GET"
        self.path = "/v1/payments/sale/{sale_id}?".replace("{sale_id}", str(sale_id))
        self.headers = {}

    
