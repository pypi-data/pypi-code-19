#!/usr/bin/env python
# Copyright 2016 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
from setuptools import setup

VERSIONFILE = "piglet/__init__.py"


def get_version():
    with open(VERSIONFILE, 'rb') as f:
        return re.search("^__version__\s*=\s*['\"]([^'\"]*)['\"]",
                           f.read().decode('UTF-8'), re.M).group(1)


def read(*path):
    """
    Return content from ``path`` as a string
    """
    with open(os.path.join(os.path.dirname(__file__), *path), 'rb') as f:
        return f.read().decode('UTF-8')


setup(name='piglet-templates',
      version=get_version(),
      description='Piglet template engine: a fast HTML template engine',
      long_description=read('README.rst') + '\n\n' + read('CHANGELOG.rst'),
      url='http://ollycope.com/software/piglet/',
      author='Oliver Cope',
      author_email='oliver@redgecko.org',
      license='Apache',
      keywords=['jinja2', 'jinja', 'genshi', 'kajiki', 'mako', 'kid',
                'html', 'template', 'templating', 'template engine'],
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Topic :: Text Processing :: Markup :: HTML'
                   ],
      install_requires=['Parsley',
                        'attrs',
                        'astunparse',
                        'markupsafe',
                        ],
      packages=['piglet'],
      include_package_data=True,
      entry_points={'babel.extractors': ['piglet=piglet.i18n:extract',
                                         'piglet_html=piglet.i18n:extract_html',
                                         'piglet_text=piglet.i18n:extract_text']}
      )
