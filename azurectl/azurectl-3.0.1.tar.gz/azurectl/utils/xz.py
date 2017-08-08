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
import lzma
import os


class XZ(object):
    """
        Implements decompression of lzma compressed files
    """
    LZMA_STREAM_BUFFER_SIZE = 8192

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lzma_stream.close()

    def __init__(self, lzma_stream, buffer_size=LZMA_STREAM_BUFFER_SIZE):
        self.buffer_size = int(buffer_size)
        self.lzma = lzma.LZMADecompressor()
        self.lzma_stream = lzma_stream
        self.buffered_bytes = b''

    def read(self, size):
        if self.lzma.eof and not self.buffered_bytes:
            return None

        chunks = self.buffered_bytes

        bytes_uncompressed = len(chunks)
        while not self.lzma.eof and bytes_uncompressed < size:
            chunks += self.lzma.decompress(
                self.lzma.unused_data + self.lzma_stream.read(self.buffer_size)
            )
            bytes_uncompressed = len(chunks)

        self.buffered_bytes = chunks[size:]
        return chunks[:size]

    @classmethod
    def close(self):
        self.lzma_stream.close()

    @classmethod
    def open(self, file_name, buffer_size=LZMA_STREAM_BUFFER_SIZE):
        self.lzma_stream = open(file_name, 'rb')
        return XZ(self.lzma_stream, buffer_size)

    @classmethod
    def uncompressed_size(self, file_name):
        with lzma.open(file_name) as lzma_stream:
            lzma_stream.seek(0, os.SEEK_END)
            return lzma_stream.tell()
