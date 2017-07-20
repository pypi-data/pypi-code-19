"""
Payline Python client library.
See ``README.md`` for usage advice.
"""
import os
import re

try:
    import setuptools
except ImportError:
    import distutils.core

    setup = distutils.core.setup
else:
    setup = setuptools.setup


PACKAGE = next((str(s) for s in setuptools.find_packages('.', exclude=("tests", "tests.*"))), None)
PWD = os.path.abspath(os.path.dirname(__file__))
VERSION = (
    re
        .compile(r".*__version__ = '(.*?)'", re.S)
        .match(open(os.path.join(PWD, PACKAGE, "__init__.py")).read())
        .group(1)
)

with open(os.path.join(PWD, "README.rst")) as f:
    README = f.read()

dependency_links = [
]

requires = [
    "finix>=1.0.17"
]

extras_require = {
    "tests": [
        "coverage==4.0.3"
    ]
}

scripts = [
    # 'bin/citadel'
]

setup(
    name=PACKAGE,
    version=VERSION,
    url='https://paylinedata.com/',
    license='MIT License',
    author='Payline Data',
    author_email='support@paylinedata.com',
    description='Payline API Python client',
    long_description=README,
    packages=[PACKAGE],
    test_suite='nose.collector',
    tests_require=extras_require['tests'],
    install_requires=requires,
    dependency_links=dependency_links,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    include_package_data=True,
    zip_safe=False,
    scripts=scripts,
    extras_require=extras_require,
    setup_requires=['nose>=1.3.7']
)
