# This class was generated on Mon, 31 Jul 2017 18:51:41 UTC by version 0.1 of Braintree SDK Generator
# sale_get_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"sale.get","Description":"Shows details for a sale, by ID. Returns only sales that were created through the REST API.\u003cbr/\u003e\u003cbr/\u003eA successful request returns the HTTP `200 OK` status code and a JSON response body that shows sale details.","QueryParameters":[],"HeaderParameters":[],"FormParameters":[],"PathParameters":[{"Type":"string","VariableName":"sale_id","Description":"The ID of the sale for which to show details.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null}],"RequestType":null,"ResponseType":{"Type":"Sale","VariableName":"","Description":"A sale transaction. Returned as a part of payment-related resources.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"GET","Path":"/v1/payments/sale/{sale_id}","ExpectedStatusCode":200}



class SaleGetRequest:
    """
    Shows details for a sale, by ID. Returns only sales that were created through the REST API.<br/><br/>A successful request returns the HTTP `200 OK` status code and a JSON response body that shows sale details.
    """

    def __init__(self, sale_id):
        self.verb = "GET"
        self.path = "/v1/payments/sale/{sale_id}?".replace("{sale_id}", str(sale_id))
        self.headers = {}
        self.headers["Content-Type"] = "application/json"
        self.body = {}

    
