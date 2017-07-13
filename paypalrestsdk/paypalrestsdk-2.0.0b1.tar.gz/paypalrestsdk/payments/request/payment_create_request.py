# This class was generated on Thu, 06 Jul 2017 16:03:30 PDT by version 0.01 of Braintree SDK Generator
# payment_create_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"payment.create","Description":"Creates a sale, an authorized payment to be captured later, or an order.\u003cbr/\u003e\u003cbr/\u003eTo create a sale, authorization, or order, include the payment details in the JSON request body. Set the `intent` to `sale`, `authorize`, or `order`. Include payer, transaction details, and, for PayPal payments only, redirect URLs. The combination of the `payment_method` and `funding_instrument` determines the type of payment that is created.\u003cbr/\u003e\u003cbr/\u003eFor more information, see [Payments REST API](/docs/integration/direct/payments/).\u003cblockquote\u003e\u003cstrong\u003eNotes:\u003c/strong\u003e \u003cul\u003e\u003cli\u003e\u003cp\u003e[Some countries](/docs/integration/direct/payments/country-currency-support/#direct-credit-card-payments) restrict direct credit card payment and related features.\u003c/p\u003e\u003c/li\u003e\u003cli\u003e\u003cp\u003eAuthorizations are guaranteed for up to three days, though you can attempt to capture an authorization for up to 29 days. After the three-day honor period authorization expires, you can [reauthorize](#authorization_reauthorize) the payment.\u003c/p\u003e\u003c/li\u003e\u003c/ul\u003e\u003c/blockquote\u003e","Parameters":[],"RequestType":{"Type":"Payment","VariableName":"body","Description":"A payment. Use this object to create, process, and manage payments.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ResponseType":{"Type":"Payment","VariableName":"","Description":"A payment. Use this object to create, process, and manage payments.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"POST","Path":"/v1/payments/payment","ExpectedStatusCode":200}



class PaymentCreateRequest:
    """
    Creates a sale, an authorized payment to be captured later, or an order.<br/><br/>To create a sale, authorization, or order, include the payment details in the JSON request body. Set the `intent` to `sale`, `authorize`, or `order`. Include payer, transaction details, and, for PayPal payments only, redirect URLs. The combination of the `payment_method` and `funding_instrument` determines the type of payment that is created.<br/><br/>For more information, see [Payments REST API](/docs/integration/direct/payments/).<blockquote><strong>Notes:</strong> <ul><li><p>[Some countries](/docs/integration/direct/payments/country-currency-support/#direct-credit-card-payments) restrict direct credit card payment and related features.</p></li><li><p>Authorizations are guaranteed for up to three days, though you can attempt to capture an authorization for up to 29 days. After the three-day honor period authorization expires, you can [reauthorize](#authorization_reauthorize) the payment.</p></li></ul></blockquote>
    """

    def __init__(self):
        self.verb = "POST"
        self.path = "/v1/payments/payment?"
        self.headers = {}

    
    
    def body(self, body):
        self.body = body
        self.headers["Content-Type"] = "application/json"
