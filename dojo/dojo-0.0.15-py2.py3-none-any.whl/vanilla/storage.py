from __future__ import absolute_import, print_function, unicode_literals

from dojo.storage import Storage


class VanillaStorage(Storage):

    def read(self):
        raise NotImplementedError()

    def write(self, path, rows, format='json', prefix='output'):
        raise NotImplementedError()
