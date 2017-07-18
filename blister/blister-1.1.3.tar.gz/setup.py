import setuptools
from distutils.command.install import INSTALL_SCHEMES
import re


# This allows "data_files" in the setup call. Thanks distutils!
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']


setuptools.setup(
    name='blister',
    version='1.1.3',
    license='MIT',
    keywords='import hook file stat disk',
    description='Import hook that minimizes file stats',

    author='Peter Shinners',
    author_email='pete@shinners.org',
    url='https://gitlab.com/shredwheat/blister',
    long_description=open("readme.md").read(),

    py_modules=["blister"],
    data_files=[('', ['license.txt'])],
    zip_safe=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
    ],   # https://pypi.python.org/pypi?%3Aaction=list_classifiers
)
