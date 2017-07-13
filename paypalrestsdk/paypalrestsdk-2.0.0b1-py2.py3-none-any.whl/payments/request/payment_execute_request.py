# This class was generated on Thu, 06 Jul 2017 16:03:30 PDT by version 0.01 of Braintree SDK Generator
# payment_execute_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"payment.execute","Description":"Executes a PayPal payment that the customer has approved. You can optionally update one or more transactions when you execute the payment.\u003cblockquote\u003e\u003cstrong\u003eImportant:\u003c/strong\u003e This call works only after a customer has approved the payment. For more information, learn about [PayPal payments](/docs/integration/direct/payments/paypal-payments/).\u003c/blockquote\u003e","Parameters":[{"Type":"string","VariableName":"payment_id","Description":"The ID of the payment to execute.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null,"Location":"path"}],"RequestType":{"Type":"Payment Execution","VariableName":"body","Description":"Executes a PayPal account-based payment with the `payer_id` obtained from the web approval URL.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ResponseType":{"Type":"Payment","VariableName":"","Description":"A payment. Use this object to create, process, and manage payments.","IsArray":false,"ReadOnly":false,"Required":false,"Properties":null},"ContentType":"application/json","HttpMethod":"POST","Path":"/v1/payments/payment/{payment_id}/execute","ExpectedStatusCode":200}



class PaymentExecuteRequest:
    """
    Executes a PayPal payment that the customer has approved. You can optionally update one or more transactions when you execute the payment.<blockquote><strong>Important:</strong> This call works only after a customer has approved the payment. For more information, learn about [PayPal payments](/docs/integration/direct/payments/paypal-payments/).</blockquote>
    """

    def __init__(self, payment_id):
        self.verb = "POST"
        self.path = "/v1/payments/payment/{payment_id}/execute?".replace("{payment_id}", str(payment_id))
        self.headers = {}

    
    
    def body(self, body):
        self.body = body
        self.headers["Content-Type"] = "application/json"
