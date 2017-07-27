from setuptools import setup

# setup(
#     name='DataExtraction',   # This is the name of your PyPI-package.\
#      version='0.1',                          # Update the version number for new releases
#      scripts=['DataExtractionTool']                  # The name of your scipt, and also the command you'll be using for calling it
#  )

import codecs
import os
import sys
import tempfile
import tarfile

#sys.path.append('/Users/yanyunliu/PycharmProjects/CourseraCrawl/DataExtraction/')
# try:
#     from setuptools import setup
# except:
#     from distutils.core import setup

from distutils.core import setup


# Get location of this file at runtime
global HERE
HERE = os.path.abspath(os.curdir)


print "There is the current path",HERE
#
# # Eval the version tuple and string from the source
# VERSION_NS = {}
# with open(os.path.join(HERE, 'jupyter_cms', '_version.py')) as f:
#     exec(f.read(), {}, VERSION_NS)



def read(fname):
    return codecs.open(os.path.join(HERE, fname)).read()

# def read(fname):
#     return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()


NAME = 'ExtractionTool'

PACKAGES = ["ExtractionTool"]

DESCRIPTION = "this is a test package."


LONG_DESCRIPTION = read("README.rst")

KEYWORDS = "test python package"

AUTHOR = "YanyunDoris"

AUTHOR_EMAIL = "dorisliu9318@gmail.com"

#
URL = "https://github.com/yanyundoris/DataExtraction"
DOWNLOAD = 'https://github.com/yanyundoris/DataExtraction/archive/0.1.tar.gz'

VERSION = "1.0.19"


LICENSE = "MIT"


setup(
    name=NAME,
    scripts=['ExtractionTool/DataExtractionTool.py'],
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords=KEYWORDS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    url= URL,
    packages=PACKAGES,
    package_dir={'ExtractionTool': 'ExtractionTool'},
    include_package_data=True,
    zip_safe=True,
    download_url=DOWNLOAD
)
