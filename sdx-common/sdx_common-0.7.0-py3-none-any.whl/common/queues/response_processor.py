from json import loads
import xml.etree.ElementTree as etree

from cryptography.fernet import Fernet
from requests import session as requests_session
from requests.packages.urllib3.exceptions import MaxRetryError

from sdx.common.exceptions import BadMessageError, RetryableError, DecryptError


class ResponseProcessor:
    """This is a response processor that decrypts/encrypts, validates and
    receipts a reponse message.

    On calling process with a message, it attempts to decrypt that message.
    Should decryption fail a DecryptError exception is raised. Decrypted
    messages are validated, with BadMessage exceptions raised should the
    message fail validation.

    Validated messages are encoded and receipted.

    """

    def __init__(self,
                 logger,
                 receipt_host,
                 receipt_path,
                 receipt_user,
                 receipt_pass,
                 session=None):
        """Create a new instance of the ResponseProcessor class

        :param logger: A reference to a logging.Logger instance
        :param receipt_host: Hostname of the receipt endpoint
        :param receipt_path: Path on receipt_host to post data
        :param receipt_user: Username for login
        :param receipt_pass: Password for receipt_user
        :param session: Requests session (optional). Defaults to None.

        :returns: Object of type ResponseProcessor
        :rtype: ResponseProcessor

        """
        self.logger = logger
        self.tx_id = ""
        self._receipt_host = receipt_host
        self._receipt_path = receipt_path
        self._receipt_user = receipt_user
        self._receipt_pass = receipt_pass

        if not session:
            self._session = requests_session()
        else:
            self._session = session

    def process(self, message, secret):
        """
        Processes a response message in the following order: 1. Decrypts
        message, validates message, encodes it and receipts the data
        against the relevant service.

        :param message: A response message
        :param secret: Secret key for decrypting message

        :returns: None

        """
        try:
            message = self._decrypt(token=message,
                                    secret=secret)
        except Exception as e:
            self.logger.error("Exception decrypting message", exception=e)
            raise DecryptError("Failed to decrypt")

        decrypted_json = loads(message)
        self._validate(decrypted_json)

        data = self._encode(decrypted_json)
        self._send_receipt(decrypted_json,
                           data)
        return

    def _validate(self, decrypted):
        """
        Validates a decrypted message.

        :param decrypted: A decrypted response message

        :returns: None

        """
        try:
            self.tx_id = decrypted['tx_id']
        except KeyError as e:
            self.tx_id = ""
            self.logger.error("No tx_id in decrypted response.", error=e)
            raise BadMessageError("Missing tx_id")

        try:
            decrypted['metadata']
        except KeyError as e:
            self.tx_id = ""
            self.logger.error("No metadata in decrypted response.", error=e)
            raise BadMessageError("Missing metadata")

        self.logger = self.logger.bind(tx_id=self.tx_id)

        try:
            decrypted['metadata']['ru_ref']
        except KeyError as e:
            self.tx_id = ""
            self.logger.error("No ru_ref in metadata", error=e)
            raise BadMessageError("Missing ru_ref in metadata")
        return

    def _decrypt(self, token, secret):
        """
        Decrypts a response message.

        :param token: Message token to decrypt
        :param secret: Secret key

        :returns: Decrypted message

        """
        f = Fernet(secret)
        try:
            message = f.decrypt(token)
        except TypeError:
            message = f.decrypt(token.encode("utf-8"))
        return message.decode("utf-8")

    def _encode(self, decrypted):
        """
        Encodes a response message.

        :param decrypted: A decrypted response message

        :returns: Encoded dictionary of form {'caseRef': ru_ref}
        :rtype: Dict

        """
        if 'metadata' in decrypted and 'ru_ref' in decrypted['metadata']:
            return {'caseRef': decrypted['metadata']['ru_ref']}
        raise BadMessageError('Missing metadata')

    def _send_receipt(self,
                      decrypted,
                      data,):
        """
        Posts a decrypted, validated and encoded message to a receipting
        service.

        :param decrypted: A decrypted response message
        :param data: Data to post to the endpoint

        :returns: Encoded dictionary of form {'caseRef': ru_ref}
        :rtype: Dict

        """
        endpoint = self._receipt_host + "/" + self._receipt_path
        if endpoint == "/":
            raise BadMessageError("Unable to determine delivery endpoint from message")

        headers = {'content-type': 'application/json'}
        auth = (self._receipt_user, self._receipt_pass)

        res_logger = self.logger.bind(request_url=endpoint)

        try:
            res_logger.info("Calling service", service="CTP_RECEIPT_HOST")
            res = self._session.post(endpoint,
                                     json=data,
                                     headers=headers,
                                     verify=False,
                                     auth=auth)

            res_logger = res_logger.bind(status=res.status_code)

            if res.status_code == 400:
                res_logger.error("Receipt rejected by endpoint")
                raise BadMessageError("Receipt rejected by endpoint")

            elif res.status_code == 404:
                namespaces = {'error': 'http://ns.ons.gov.uk/namespaces/resources/error'}
                tree = etree.fromstring(res.content)
                element = tree.find('error:message', namespaces).text
                elements = element.split('-')

                if elements[0] == '1009':
                    stat_unit_id = elements[-1].split('statistical_unit_id: ')[-1].split()[0]
                    collection_exercise_sid = elements[-1].split('collection_exercise_sid: ')[-1].split()[0]  # noqa

                    res_logger.error("Receipt rejected by endpoint",
                                     msg="No records were found on the man_ce_sample_map table",
                                     error=1009,
                                     stat_unit_id=stat_unit_id,
                                     collection_exercise_sid=collection_exercise_sid)

                    raise BadMessageError("Receipt rejected by endpoint")

                else:
                    res_logger.error("Bad response from endpoint")
                    raise RetryableError("Bad response from endpoint")

            elif res.status_code != 200 and res.status_code != 201:
                # Endpoint may be temporarily down
                res_logger.error("Bad response from endpoint")
                raise RetryableError("Bad response from endpoint")

            else:
                res_logger.info("Sent receipt")
                return

        except MaxRetryError:
            res_logger.error("Max retries exceeded (5) attempting to send to endpoint")
            raise RetryableError("Failure to send receipt")
