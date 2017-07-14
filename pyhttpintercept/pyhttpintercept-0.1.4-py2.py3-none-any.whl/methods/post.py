
import cgi
import logging_helper
from .base import BaseRequestHandler


logging = logging_helper.setup_logging()


class PostHandler(BaseRequestHandler):

    method_type = u'post'

    def __init__(self,
                 *args,
                 **kwargs):
        super(PostHandler, self).__init__(*args, **kwargs)

    def handle(self):

        # TODO: Test against Form submission
        # (Only tried with JSON)

        # try:
        #     form = cgi.FieldStorage(
        #         fp=self.rfile,
        #         headers=self.headers,
        #         environ={u'REQUEST_METHOD': u'POST',
        #                  u'CONTENT_TYPE':   self.headers[u'Content-Type'],
        #                  })
        #     logging.warning(u"======= POST VALUES =======")
        #     if form.list:
        #         for item in form.list:
        #             logging.warning(item)
        #     logging.warning(u"\n")
        # except:
        #     pass

        content_length = int(self.__request.headers.getheader(u'content-length', -1))
        if content_length != -1:
            body = self.__request.rfile.read(content_length)
        else:
            body = self.__request.rfile.read()  # read all??

        post_data = {u'data': body}

        logging.info(u'POST data:{body}'.format(body=body))
