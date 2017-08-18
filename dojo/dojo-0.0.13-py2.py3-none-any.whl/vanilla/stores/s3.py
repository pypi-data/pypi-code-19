from __future__ import absolute_import, print_function, unicode_literals

from ..storage import Storage


class VanillaS3Store(Storage):

    def read(self):
        raise NotImplementedError()

    def write(self, rows):
        raise NotImplementedError()
