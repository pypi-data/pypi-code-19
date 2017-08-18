from __future__ import absolute_import, print_function, unicode_literals

from dojo.transform import Transform


class DeKey(Transform):

    def process(self, key_value):
        return key_value[1]
