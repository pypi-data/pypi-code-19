# Copyright (c) 2015 SUSE Linux GmbH.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from azure.storage.file import FileService

# project
from azurectl.azurectl_exceptions import (
    AzureFileShareListError,
    AzureFileShareCreateError,
    AzureFileShareDeleteError
)


class FileShare(object):
    """
        Information from Azure files service
    """
    def __init__(self, account):
        self.account_name = account.storage_name()
        self.account_key = account.storage_key()
        self.files = FileService(
            self.account_name, self.account_key
        )

    def list(self):
        """
            list file shares
        """
        result = []
        try:
            for share in self.files.list_shares():
                result.append(format(share.name))
        except Exception as e:
            raise AzureFileShareListError(
                '%s: %s' % (type(e).__name__, format(e))
            )
        return result

    def create(self, share_name):
        """
            create a file share
        """
        try:
            self.files.create_share(share_name)
        except Exception as e:
            raise AzureFileShareCreateError(
                '%s: %s' % (type(e).__name__, format(e))
            )

    def delete(self, share_name):
        """
            delete a file share
        """
        try:
            self.files.delete_share(share_name)
        except Exception as e:
            raise AzureFileShareDeleteError(
                '%s: %s' % (type(e).__name__, format(e))
            )
