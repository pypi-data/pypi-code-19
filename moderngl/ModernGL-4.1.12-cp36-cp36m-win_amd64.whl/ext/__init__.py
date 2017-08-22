'''
    ModernGL extensions
'''

# pylint: disable=R0903, W0613

import os
import sys


class ExtensionFinder():
    '''
        ExtensionFinder
    '''

    def find_spec(self, fullname, path, target=None):
        '''
            find_spec
        '''

        prefix = 'ModernGL.ext.'

        if fullname.startswith(prefix):
            name = fullname[len(prefix):]
            if '.' in name:
                return

            here = os.path.dirname(__file__)
            path = os.path.join(here, name)

            if not os.path.isdir(path):
                local = os.path.isfile(os.path.join(here, 'README.md'))

                if local:
                    error = 'missing extension\n\nDo not run ModernGL from the git repository!'

                else:
                    error = 'missing extension\n\nHint: python3 -m pip install %s' % fullname

                raise ModuleNotFoundError(error)


sys.meta_path.append(ExtensionFinder())
