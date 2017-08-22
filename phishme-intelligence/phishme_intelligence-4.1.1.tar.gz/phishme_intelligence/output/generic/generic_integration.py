"""
Copyright 2013-2017 PhishMe, Inc.  All rights reserved.

This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.
"""

from phishme_intelligence.output.base_integration import BaseIntegration


class GenericIntegration(BaseIntegration):

    def process(self, mrti, threat_id):
        """

        :param mrti:
        :param threat_id:
        :return:
        """

        if self.config.getboolean(self.product, 'append_file_use'):
            self._file_append(mrti)

        if self.config.getboolean(self.product, 'multiple_file_use'):
            self._file_write(mrti, threat_id)
