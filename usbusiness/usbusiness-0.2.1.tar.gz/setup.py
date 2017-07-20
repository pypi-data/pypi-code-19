from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='usbusiness',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version='0.2.01',
    # setup_requires = [
    #     'scipy>=0.19.1',
    #     'numpy>=1.13.1',
    # ],
    install_requires = [
        'pyenchant>=1.6.8',
        'requests>=2.18.1',
        'requests>=2.18.1',
        'bs4>=0.0.1',
        'tldextract>=2.1.0'
        # 'scikit-learn>=0.18.2',
        # 'scipy>=0.19.1',
        # 'numpy>=1.13.1',
    ],
    description='NAICS code business domain classifier and domain utility kit',
    long_description=long_description,  #this is the

    # The project's main homepage.
    # url='https://github.com/whatever/whatever',

    # Author details
    author='Glendon Thompson',
    author_email='glendonthompson1@gmail.com',

    # Choose your license
    license='MIT',

    # See https://PyPI.python.org/PyPI?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ],

    python_requires='>=2.7',

    # What does your project relate to?
    keywords='naics usa business predict website analytics industry classfication',

    packages=["usbusiness"],

    include_package_data=True,

    package_data={
        'usbusiness':['Makefile'],
        'data':
             ['data/google_100k.txt',
             'data/naics_codes_2012.csv',
            #  'data/site_clf.sk',
             'data/stop_words.txt',
             ]
    },

)
