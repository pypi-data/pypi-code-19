# This class was generated on Mon, 31 Jul 2017 18:51:41 UTC by version 0.1 of Braintree SDK Generator
# payment_create_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"payment.create","Description":"Creates a sale, an authorized payment to be captured later, or an order.\u003cbr/\u003e\u003cblockquote\u003e\u003cstrong\u003eImportant:\u003c/strong\u003e The use of the PayPal REST \u003ccode\u003e/payments\u003c/code\u003e APIs to accept credit card payments is restricted. Instead, you can accept credit card payments with:\u003cul\u003e\u003cli\u003e\u003ca href=\"/docs/integration/direct/payments/guest-payments/\"\u003eGuest payments\u003c/a\u003e with a \u003ca href=\"/docs/api/vault/#credit-card_create\"\u003ecredit card that is stored in the PayPal vault\u003c/a\u003e\u003c/li\u003e\u003cli\u003e\u003ca href=\"https://www.braintreepayments.com/products/braintree-direct\"\u003eBraintree Direct\u003c/a\u003e\u003c/li\u003e\u003cli\u003e\u003ca href=\"https://www.paypal.com/us/webapps/mpp/merchant\"\u003ePayPal business products\u003c/a\u003e\u003c/li\u003e\u003c/ul\u003e\u003c/blockquote\u003e\u003cbr/\u003eTo create a sale, authorization, or order, include the payment details in the JSON request body. Set the `intent` to `sale`, `authorize`, or `order`. Include payer, transaction details, and redirect URLs. The combination of the `payment_method` and `funding_instrument` determines the type of payment that is created.\u003cbr/\u003e\u003cbr/\u003eA successful request returns the HTTP `201 Created` status code and a JSON response body that shows payment details.\u003cbr/\u003e\u003cbr/\u003eFor more information, see [Payments REST API](/docs/integration/direct/payments/).\u003cblockquote\u003e\u003cstrong\u003eNote:\u003c/strong\u003e \u003cul\u003eAuthorizations are guaranteed for up to three days, though you can attempt to capture an authorization for up to 29 days. After the three-day honor period authorization expires, you can [reauthorize](#authorization_reauthorize) the payment.\u003c/blockquote\u003e","QueryParameters":[],"HeaderParameters":[],"FormParameters":[],"PathParameters":[],"RequestType":{"Type":"Payment","VariableName":"body","Description":"A payment. Use this object to create, process, and manage payments.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ResponseType":{"Type":"Payment","VariableName":"","Description":"A payment. Use this object to create, process, and manage payments.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"POST","Path":"/v1/payments/payment","ExpectedStatusCode":200}



class PaymentCreateRequest:
    """
    Creates a sale, an authorized payment to be captured later, or an order.<br/><blockquote><strong>Important:</strong> The use of the PayPal REST <code>/payments</code> APIs to accept credit card payments is restricted. Instead, you can accept credit card payments with:<ul><li><a href="/docs/integration/direct/payments/guest-payments/">Guest payments</a> with a <a href="/docs/api/vault/#credit-card_create">credit card that is stored in the PayPal vault</a></li><li><a href="https://www.braintreepayments.com/products/braintree-direct">Braintree Direct</a></li><li><a href="https://www.paypal.com/us/webapps/mpp/merchant">PayPal business products</a></li></ul></blockquote><br/>To create a sale, authorization, or order, include the payment details in the JSON request body. Set the `intent` to `sale`, `authorize`, or `order`. Include payer, transaction details, and redirect URLs. The combination of the `payment_method` and `funding_instrument` determines the type of payment that is created.<br/><br/>A successful request returns the HTTP `201 Created` status code and a JSON response body that shows payment details.<br/><br/>For more information, see [Payments REST API](/docs/integration/direct/payments/).<blockquote><strong>Note:</strong> <ul>Authorizations are guaranteed for up to three days, though you can attempt to capture an authorization for up to 29 days. After the three-day honor period authorization expires, you can [reauthorize](#authorization_reauthorize) the payment.</blockquote>
    """

    def __init__(self):
        self.verb = "POST"
        self.path = "/v1/payments/payment?"
        self.headers = {}
        self.headers["Content-Type"] = "application/json"
        self.body = {}

    
    
    def requestBody(self, body):
        self.body = body
        return self
