# This class was generated on Thu, 06 Jul 2017 16:03:37 PDT by version 0.01 of Braintree SDK Generator
# invoice_delete_request.py
# DO NOT EDIT
# @type request
# @json {"Name":"invoice.delete","Description":"Deletes a draft invoice, by ID. Deletes invoices in the draft state only. For invoices that have already been sent, you can [cancel the invoice](/docs/api/invoicing/#invoices_cancel). After you delete a draft invoice, you can no longer use it or show its details. However, you can reuse its invoice number.","Parameters":[{"Type":"string","VariableName":"invoice_id","Description":"The ID of the invoice to delete.","IsArray":false,"ReadOnly":false,"Required":true,"Properties":null,"Location":"path"}],"RequestType":null,"ResponseType":null,"ContentType":"application/json","HttpMethod":"DELETE","Path":"/v1/invoicing/invoices/{invoice_id}","ExpectedStatusCode":200}



class InvoiceDeleteRequest:
    """
    Deletes a draft invoice, by ID. Deletes invoices in the draft state only. For invoices that have already been sent, you can [cancel the invoice](/docs/api/invoicing/#invoices_cancel). After you delete a draft invoice, you can no longer use it or show its details. However, you can reuse its invoice number.
    """

    def __init__(self, invoice_id):
        self.verb = "DELETE"
        self.path = "/v1/invoicing/invoices/{invoice_id}?".replace("{invoice_id}", str(invoice_id))
        self.headers = {}

    
