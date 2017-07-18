# pylint: disable=C0330
import os.path

import setuptools

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
README_PATH = os.path.join(ROOT_DIR, 'README')

with open(README_PATH, encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setuptools.setup(
    name='ezvalue',
    version='0.1.2',
    description='An elegant and powerfull implementation of a value object.',
    long_description=LONG_DESCRIPTION,

    url='https://github.com/snah/ezvalue',

    author='Hans Maree',
    author_email='hans.maree@gmail.com',

    license='MIT',

    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Topic :: Software Development',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.2',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 ],

    keywords='value valueobject immutable',

    packages=['ezvalue'],
)
