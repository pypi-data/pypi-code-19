import unittest
import responses
import base64
import json

from paypalrestsdk.core import PayPalHttpClient
from paypalrestsdk.core.test.paypaltestharness import PayPalTestHarness


class SimpleRequest:

    def __init__(self, path="/", verb="GET"):
        self.path = path
        self.verb = verb
        self.headers = {}


class PayPalHttpClientTest(PayPalTestHarness):

    def setUp(self):
        self.client = PayPalHttpClient(self.environment())

    @responses.activate
    def testPayPalHttpClient_execute_fetchesAccessTokenIfNone(self):
        request = SimpleRequest("/", "POST")
        self.stub_request_with_response(request)
        self.stubaccesstokenrequest()

        self.client.execute(request)

        self.assertEqual(2, len(responses.calls))

        accesstokenrequest = responses.calls[0].request
        self.assertEqual(self.environment().base_url() + "/v1/oauth2/token", accesstokenrequest.url)
        self.assertEqual("application/x-www-form-urlencoded", accesstokenrequest.headers["Content-Type"])

        expectedauthheader ="Basic {0}".format(base64.b64encode(("{0}:{1}".format(self.environment().client_id, self.environment().client_secret)).encode()).decode())
        self.assertEqual(expectedauthheader, accesstokenrequest.headers["Authorization"])
        self.assertEqual("grant_type=client_credentials", accesstokenrequest.body)

    @responses.activate
    def testPayPalHttpClient_execute_fetchesAccessTokenIfExpired(self):
        request = SimpleRequest("/", "POST")
        self.stub_request_with_response(request)

        self.client._access_token = self.simpleaccesstoken()
        self.client._access_token.expires_in = 0

        self.stubaccesstokenrequest()

        self.client.execute(request)

        self.assertEqual(2, len(responses.calls))

        accesstokenrequest = responses.calls[0].request
        self.assertEqual(self.environment().base_url() + "/v1/oauth2/token", accesstokenrequest.url)

    @responses.activate
    def testPayPalHttpClient_withRefreshToken_fetchesAccessTokenWithRefreshToken(self):
        request = SimpleRequest("/", "POST")
        self.stub_request_with_response(request)

        self.client = PayPalHttpClient(self.environment(), refresh_token="refresh-token")

        self.stubaccesstokenrequest(refresh_token="refresh-token")

        self.client.execute(request)

        self.assertEqual(2, len(responses.calls))

        accesstokenrequest = responses.calls[0].request
        self.assertEqual(self.environment().base_url() + "/v1/identity/openidconnect/tokenservice", accesstokenrequest.url)
        self.assertEqual("application/x-www-form-urlencoded", accesstokenrequest.headers["Content-Type"])

        expectedauthheader ="Basic {0}".format(base64.b64encode(("{0}:{1}".format(self.environment().client_id, self.environment().client_secret)).encode()).decode())
        self.assertEqual(expectedauthheader, accesstokenrequest.headers["Authorization"])
        self.assertEqual("grant_type=client_credentials&refresh_token=refresh-token", accesstokenrequest.body)

    @responses.activate
    def testPayPalHttpClient_execute_setsCommonHeaders_and_signsRequest(self):
        self.client._access_token = self.simpleaccesstoken()

        request = SimpleRequest("/", "POST")
        self.stub_request_with_response(request)

        self.client.execute(request)

        self.assertEqual(len(responses.calls), 1)

        actualrequest = responses.calls[0].request
        self.assertEqual(actualrequest.headers["Accept-Encoding"], "gzip")
        self.assertEqual(actualrequest.headers["Authorization"], "Bearer sample-access-token")

    @responses.activate
    def testPayPalHttpClient_execute_serializesDataWhenPresentAndContentTypeSet(self):
        self.client._access_token = self.simpleaccesstoken()

        body = {"some-key": "some-value"}
        request = SimpleRequest("/", "POST")
        request.body = body
        request.headers["Content-Type"] = "application/json"

        self.stub_request_with_response(request)

        self.client.execute(request)

        self.assertEqual(1, len(responses.calls))

        actualrequest = responses.calls[0].request

        self.assertEqual(json.dumps(body), actualrequest.body)

    @responses.activate
    def testPayPalHttpClient_execute_withRequestBody_contentTypeNotPresent_throws(self):
        self.client._access_token = self.simpleaccesstoken()

        request = SimpleRequest("/", "POST")
        request.body = {"some-key", "some-value"}
        self.stub_request_with_response(request)

        try:
            self.client.execute(request)
            self.fail("expected IOError")
        except IOError as ioe:
            self.assertTrue("Unable to serialize content" in str(ioe))

    @responses.activate
    def testPayPalHttpClient_execute_withRequestBody_contentTypeNotJson(self):
        self.client._access_token = self.simpleaccesstoken()

        request = SimpleRequest("/", "POST", )
        request.body = {"some-key", "some-value"}
        request.headers["Content-Type"] = "application/xml"

        self.stub_request_with_response(request)

        try:
            self.client.execute(request)
            self.fail("expected IOError")
        except IOError as ioe:
            self.assertTrue("Unable to serialize content" in str(ioe))

    @responses.activate
    def testPayPalHttpClient_execute_whenResponseBodyAndContentTypePresent_deserializesResponse(self):
        self.client._access_token = self.simpleaccesstoken()

        request = SimpleRequest("/", "POST")

        self.stub_request_with_response(request, {"some-key": "some-value"})

        actualresponse = self.client.execute(request)
        self.assertEqual("some-value", actualresponse.result.some_key)

    @responses.activate
    def testPayPalHttpClient_execute_whenResponseBodyAndContentTypeNotPresent_throws(self):
        self.client._access_token = self.simpleaccesstoken()

        request = SimpleRequest("/", "POST")

        self.stub_request_with_response(request, {"some-key": "some-value"}, content_type="")

        try:
            self.client.execute(request)
            self.fail("expected IOError")
        except IOError as ioe:
            self.assertTrue("Unsupported Content-Type" in str(ioe))

    @responses.activate
    def testPayPalHttpClient_execute_whenResponseBodyAndContentTypeNotJson_throws(self):
        self.client._access_token = self.simpleaccesstoken()

        request = SimpleRequest("/", "POST")
        request.body = {"some_data": "someValue"}
        request.headers["Content-Type"] = "application/json"

        self.stub_request_with_response(request, {"some_key": "some-value"}, content_type="application/xml")

        try:
            self.client.execute(request)
            self.fail("expected IOError")
        except IOError as ioe:
            self.assertTrue("Unsupported Content-Type: application/xml" in str(ioe))

if __name__ == '__main__':
    unittest.main()
