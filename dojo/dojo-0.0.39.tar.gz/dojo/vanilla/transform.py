from __future__ import absolute_import, print_function, unicode_literals

from dojo.transform import Transform


class VanillaTransform(Transform):

    def process(self, row):
        raise NotImplementedError()
