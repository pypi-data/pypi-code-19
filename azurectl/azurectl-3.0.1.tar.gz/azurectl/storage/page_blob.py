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
from azurectl.azurectl_exceptions import (
    AzurePageBlobZeroPageError,
    AzurePageBlobAlignmentViolation,
    AzurePageBlobSetupError,
    AzurePageBlobUpdateError
)


class PageBlob(object):
    """
        Page blob iterator to control a stream of data to an Azure page blob
    """
    def __init__(self, blob_service, blob_name, container, byte_size):
        """
            Create a new page blob of the specified byte_size with
            name blob_name in the specified container. An azure page
            blob must be 512 byte aligned
        """
        self.container = container
        self.blob_service = blob_service
        self.blob_name = blob_name

        self.__validate_page_alignment(byte_size)

        self.rest_bytes = byte_size
        self.page_start = 0

        try:
            self.blob_service.create_blob(
                self.container, self.blob_name, byte_size
            )
        except Exception as e:
            raise AzurePageBlobSetupError(
                '%s: %s' % (type(e).__name__, format(e))
            )

    def next(self, data_stream, max_chunk_byte_size=None, max_attempts=5):
        if not max_chunk_byte_size:
            max_chunk_byte_size = self.blob_service.MAX_CHUNK_GET_SIZE
        max_chunk_byte_size = int(max_chunk_byte_size)

        requested_bytes = min(
            self.rest_bytes, max_chunk_byte_size
        )

        if requested_bytes != max_chunk_byte_size:
            zero_page = self.__read_zero_page(requested_bytes)
        else:
            zero_page = self.__read_zero_page(max_chunk_byte_size)

        data = data_stream.read(requested_bytes)

        if not data:
            raise StopIteration()

        length = len(data)
        page_end = self.page_start + length - 1

        if not data == zero_page:
            upload_errors = []
            while len(upload_errors) < max_attempts:
                try:
                    self.blob_service.update_page(
                        self.container,
                        self.blob_name,
                        data,
                        self.page_start,
                        page_end
                    )
                    break
                except Exception as e:
                    upload_errors.append(
                        '%s: %s' % (type(e).__name__, format(e))
                    )

            if len(upload_errors) == max_attempts:
                raise AzurePageBlobUpdateError(
                    'Page update failed with: %s' % '\n'.join(upload_errors)
                )

        self.rest_bytes -= length
        self.page_start += length

        return self.page_start

    def __iter__(self):
        return self

    def __validate_page_alignment(self, byte_size):
        remainder = byte_size % 512
        if remainder != 0:
            raise AzurePageBlobAlignmentViolation(
                'Uncompressed size %d is not 512 byte aligned' % byte_size
            )

    def __read_zero_page(self, requested_bytes):
        try:
            with open('/dev/zero', 'rb') as zero_stream:
                return zero_stream.read(requested_bytes)
        except Exception as e:
            raise AzurePageBlobZeroPageError(
                'Reading zero page failed with: %s' % format(e)
            )
