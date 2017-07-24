# encoding: utf-8
import zeep


class EuromsgMailer(object):
    """
    Provides a simple interface for sending an email over euro.message service.
    """
    AUTHORIZATION_URL = "https://ws.euromsg.com/live/auth.asmx?wsdl"
    POST_URL = "https://ws.euromsg.com/live/post.asmx?wsdl"

    username = ""
    password = ""

    def __init__(self, _username, _password, _authurl=None, _posturl=None):
        self.username = _username
        self.password = _password
        if _authurl:
            self.AUTHORIZATION_URL = _authurl
        if _posturl:
            self.POST_URL = _posturl

    def send_mail(self, from_name, from_address, replyto_address, to_name, to_address, subject, message, encoding="UTF-8"):
        """
        Build and send an email according to given arguments.
        :param from_name: From name
        :param from_address: From address
        :param replyto_address: Address for replies
        :param to_name: Name to send
        :param to_address: Email address to send
        :param subject: Subject of an email
        :param message: Email's body as an HTML
        :param encoding: Encoding of email. Default: UTF-8
        :return: Euromsg's PostID
        :raise Exception: Raises an exception on unseccessful operations
        """
        client = zeep.Client(wsdl=self.AUTHORIZATION_URL)
        resp = (client.service.Login(self.username, self.password))
        try:
            ticket = resp["ServiceTicket"]
        except KeyError:
            raise Exception("There was an error with authentication!")

        client = zeep.Client(wsdl=self.POST_URL)
        post_resp = (client.service.PostHtml(
            ticket,
            from_name,
            from_address,
            replyto_address,
            subject,
            message,
            encoding,
            to_name,
            to_address,
            None
        ))

        if post_resp["Code"] == "00":
            return post_resp["PostID"]
        else:
            raise Exception("{}: {}".format(post_resp["Code"],
                                            post_resp["Message"]))
