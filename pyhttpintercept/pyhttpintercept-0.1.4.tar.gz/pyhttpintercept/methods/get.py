
import logging_helper
from .base import BaseRequestHandler


logging = logging_helper.setup_logging()


class GetHandler(BaseRequestHandler):

    method_type = u'get'

    def __init__(self,
                 *args,
                 **kwargs):
        super(GetHandler, self).__init__(*args, **kwargs)
