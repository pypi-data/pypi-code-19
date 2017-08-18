from __future__ import absolute_import, print_function, unicode_literals

from dojo.transform import Transform


class KeyBy(Transform):

    def __init__(self, key, *args, **kwargs):
        self.key = key
        self.default = kwargs.pop('default', None)
        super(KeyBy, self).__init__(*args, **kwargs)

    def process(self, row):
        return (row.get(self.key, self.default), row)
