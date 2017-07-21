from codecs import open
import os.path

from setuptools import setup, find_packages

MY_DIR_PATH = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join('..', 'java', 'pom.xml')) as pom_xml_file:
    for line in pom_xml_file:
        line = line.strip()
        if line.startswith('<version>'):
            version = line[len('<version>'):-len('</version>')]
            break
version = version.rstrip('-SNAPSHOT')
print version

setup(
    author='Minor Gordon',
    author_email='pastpy@minorgordon.net',
    name='libthryft',
    description='Runtime library for the Thryft code generation framework',
    license='BSD',
    long_description='Runtime library for the Thryft code generation framework',
    url='https://github.com/minorg/thryft',
    version=version,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    packages=find_packages('src'),
    package_dir = {'':'src'},
)
