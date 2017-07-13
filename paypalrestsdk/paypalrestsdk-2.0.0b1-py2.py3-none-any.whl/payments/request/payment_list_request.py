# This class was generated on Thu, 06 Jul 2017 16:03:30 PDT by version 0.01 of Braintree SDK Generator
# payment_list_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"payment.list","Description":"Lists payments that were created by the [create payment](#payment_create) call and that are in any state. The list shows the payments that are made to the merchant who makes the call. To filter the payments that appear in the response, you can specify one or more optional query and pagination parameters. See [Filtering and pagination](/docs/api/overview/#filtering-and-pagination).","Parameters":[{"Type":"integer","VariableName":"count","Description":"The number of items to list in the response.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null,"Location":"query"},{"Type":"string","VariableName":"end_time","Description":"The end date and time for the range to show in the response, in [Internet date and time format](https://tools.ietf.org/html/rfc3339#section-5.6). For example, `start_time=2016-03-06T11:00:00Z`.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null,"Location":"query"},{"Type":"string","VariableName":"payee_id","Description":"Filters the response by a PayPal-assigned merchant ID that identifies the payee.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null,"Location":"query"},{"Type":"string","VariableName":"sort_by","Description":"Sorts the response by the create time or update time.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null,"Location":"query"},{"Type":"string","VariableName":"sort_order","Description":"Sorts the response in ascending or descending order.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null,"Location":"query"},{"Type":"string","VariableName":"start_id","Description":"The ID of the starting resource in the response. When results are paged, you can use the `next_id` value as the `start_id` to continue with the next set of results.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null,"Location":"query"},{"Type":"integer","VariableName":"start_index","Description":"The start index of the payments to list. Typically, you use the `start_index` to jump to a specific position in the resource history based on its cart. For example, to start at the second item in a list of results, specify `?start_index=2`.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null,"Location":"query"},{"Type":"string","VariableName":"start_time","Description":"The start date and time for the  range to show in the response, in [Internet date and time format](https://tools.ietf.org/html/rfc3339#section-5.6). For example, `start_time=2016-03-06T11:00:00Z`.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null,"Location":"query"}],"RequestType":null,"ResponseType":{"Type":"Payment History ","VariableName":"","Description":"The list of payments that the seller made.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"GET","Path":"/v1/payments/payment","ExpectedStatusCode":200}



class PaymentListRequest:
    """
    Lists payments that were created by the [create payment](#payment_create) call and that are in any state. The list shows the payments that are made to the merchant who makes the call. To filter the payments that appear in the response, you can specify one or more optional query and pagination parameters. See [Filtering and pagination](/docs/api/overview/#filtering-and-pagination).
    """

    def __init__(self):
        self.verb = "GET"
        self.path = "/v1/payments/payment?"
        self.headers = {}

    def count(self, count):
        self.path += self.path + "count=" + str(count) + "&"
        return self

    def endTime(self, endTime):
        self.path += self.path + "end_time=" + str(endTime) + "&"
        return self

    def payeeId(self, payeeId):
        self.path += self.path + "payee_id=" + str(payeeId) + "&"
        return self

    def sortBy(self, sortBy):
        self.path += self.path + "sort_by=" + str(sortBy) + "&"
        return self

    def sortOrder(self, sortOrder):
        self.path += self.path + "sort_order=" + str(sortOrder) + "&"
        return self

    def startId(self, startId):
        self.path += self.path + "start_id=" + str(startId) + "&"
        return self

    def startIndex(self, startIndex):
        self.path += self.path + "start_index=" + str(startIndex) + "&"
        return self

    def startTime(self, startTime):
        self.path += self.path + "start_time=" + str(startTime) + "&"
        return self

    
