"""
 * Created by Synerty Pty Ltd
 *
 * This software is open source, the MIT license applies.
 *
 * Website : http://www.synerty.com
 * Support : support@synerty.com
"""

import logging

from twisted.web import server

from txhttputil.site.SpooledNamedTemporaryFile import SpooledNamedTemporaryFile

logger = logging.getLogger(name=__name__)


class FileUploadRequest(server.Request):
    tmpFilePath = None
    spoolSize = 5 * 1024 * 1024

    def gotLength(self, length):
        """
        Called when HTTP channel got length of content in this request.

        This method is not intended for users.

        @param length: The length of the request body, as indicated by the
            request headers.  L{None} if the request headers do not indicate a
            length.
        """
        self.content = SpooledNamedTemporaryFile(max_size=self.spoolSize,
                                                 dir=self.tmpFilePath)
